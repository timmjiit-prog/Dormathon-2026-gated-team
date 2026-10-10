#!/usr/bin/env python
"""
RootIQ SME Business Data Analyzer
==================================
A reusable, deterministic data-analysis engine for SME operational workbooks.

Reads an Excel workbook (Sales, Inventory, Purchase_Orders, Suppliers,
Customer_Feedback, and optionally Operations), validates schema, parses dates
and numerics safely, reports data-quality issues, compares a BASELINE period
against a CURRENT period, computes business metrics, detects anomalies using
configurable rules, ranks them by magnitude and business relevance, and emits
structured JSON + CSV.

No root-cause reasoning.  No LLM estimation.  Every number comes from code.

Usage
-----
    from rootiq_analyzer import RootIQAnalyzer

    analyzer = RootIQAnalyzer("path/to/workbook.xlsx")
    result = analyzer.run()
    # result is a dict matching the output schema; files are also saved to disk.

Command line
------------
    python rootiq_analyzer.py <workbook.xlsx> [--out-dir <dir>]

Output files
------------
    analysis_summary.json   — full structured result
    analysis_summary.csv    — flat metrics table (one row per metric)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import warnings
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd

# ──────────────────────────────────────────────────────────────────────────
# 1. Configuration
# ──────────────────────────────────────────────────────────────────────────

BASELINE_PERIOD = (date(2026, 8, 3), date(2026, 8, 30))
CURRENT_PERIOD = (date(2026, 8, 31), date(2026, 9, 27))
PERIOD_DAYS = 28  # both windows are 28 days, inclusive

# Expected sheets and their required columns.  Unknown sheets (e.g. Operations)
# are loaded but not required to match any schema.
EXPECTED_SHEETS: dict[str, list[str]] = {
    "Sales": ["date", "order_id", "product_id", "quantity", "unit_price", "revenue"],
    "Inventory": ["date", "product_id", "opening_stock", "received", "sold",
                  "closing_stock", "stockout_hours"],
    "Purchase_Orders": ["po_id", "product_id", "supplier_id", "request_date",
                        "approval_date", "order_date", "delivery_date",
                        "quantity", "status", "approval_days",
                        "supplier_lead_days"],
    "Suppliers": ["supplier_id", "product_id", "expected_lead_time_days",
                  "baseline_avg_lead_days", "current_avg_lead_days",
                  "baseline_unit_cost", "current_unit_cost",
                  "on_time_delivery_rate_pct"],
    "Customer_Feedback": ["date", "feedback_id", "product_id", "complaint_type",
                          "rating", "refund", "order_cancelled"],
}

# Date columns per sheet
DATE_COLUMNS: dict[str, list[str]] = {
    "Sales": ["date"],
    "Inventory": ["date"],
    "Purchase_Orders": ["request_date", "approval_date", "order_date",
                        "delivery_date"],
    "Customer_Feedback": ["date"],
}

# Numeric columns per sheet
NUMERIC_COLUMNS: dict[str, list[str]] = {
    "Sales": ["quantity", "unit_price", "revenue"],
    "Inventory": ["opening_stock", "received", "sold", "closing_stock",
                  "stockout_hours"],
    "Purchase_Orders": ["quantity", "approval_days", "supplier_lead_days"],
    "Suppliers": ["expected_lead_time_days", "baseline_avg_lead_days",
                  "current_avg_lead_days", "baseline_unit_cost",
                  "current_unit_cost", "on_time_delivery_rate_pct"],
    "Customer_Feedback": ["rating"],
}

# ── Anomaly thresholds (user-specified) ──────────────────────────────────

ANOMALY_RULES: dict[str, dict] = {
    "revenue": {"type": "pct_le", "threshold": -10.0, "relevance": 10,
                "label": "Revenue decline"},
    "product_revenue": {"type": "pct_le", "threshold": -15.0, "relevance": 9,
                       "label": "Product revenue decline"},
    "stockout_hours": {"type": "stockout", "threshold_mult": 2.0,
                       "threshold_abs": 8.0, "relevance": 8,
                       "label": "Stockout hours surge"},
    "po_approval_time": {"type": "approval", "threshold_abs": 2.0,
                         "threshold_mult": 1.5, "relevance": 7,
                         "label": "PO approval time spike"},
    "supplier_lead_time": {"type": "mult_gt", "threshold": 1.5,
                           "relevance": 7, "label": "Supplier lead-time increase"},
    "unit_cost": {"type": "pct_ge", "threshold": 10.0, "relevance": 5,
                  "label": "Unit-cost increase"},
    "complaint_rate": {"type": "pct_ge", "threshold": 50.0, "relevance": 6,
                       "label": "Complaint-rate increase"},
    "refund_rate": {"type": "pct_ge", "threshold": 50.0, "relevance": 6,
                    "label": "Refund-rate increase"},
    "fulfilment_time": {"type": "pct_ge", "threshold": 30.0, "relevance": 7,
                        "label": "Fulfilment-time increase"},
    "late_orders": {"type": "pct_ge", "threshold": 50.0, "relevance": 7,
                    "label": "Late-order increase"},
}

# Severity bands based on composite score (magnitude × relevance)
SEVERITY_BANDS = [
    (100, "critical"),
    (50, "high"),
    (20, "medium"),
    (1, "low"),
]


# ──────────────────────────────────────────────────────────────────────────
# 2. Helpers
# ──────────────────────────────────────────────────────────────────────────

def _to_date(val: Any) -> date | None:
    """Safely convert a value to date.  Handles Excel serials, strings,
    datetime objects, and already-date values."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    if isinstance(val, (int, float)):
        # Excel serial date (days since 1899-12-30)
        try:
            return (datetime(1899, 12, 30) + timedelta(days=int(val))).date()
        except (ValueError, OverflowError):
            return None
    s = str(val).strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y",
                "%m/%d/%Y", "%Y%m%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s).date()
    except (ValueError, TypeError):
        return None


def _safe_num(val: Any) -> float | None:
    """Safely convert to float, returning None for non-numeric."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    try:
        return float(str(val).strip())
    except (ValueError, TypeError):
        return None


def _pct_change(base: float | None, cur: float | None) -> tuple[float | None, bool]:
    """Relative percentage change.  Returns (value, base_zero_flag)."""
    if base is None or cur is None:
        return None, False
    if base == 0:
        return None, True
    return (cur - base) / base * 100.0, False


def _pp_change(base: float | None, cur: float | None) -> float | None:
    """Absolute percentage-point change (for rates)."""
    if base is None or cur is None:
        return None
    return cur - base


def _round(v: float | None, dp: int = 2) -> float | None:
    if v is None:
        return None
    return round(v, dp)


def _severity(score: float) -> str:
    for threshold, label in SEVERITY_BANDS:
        if score >= threshold:
            return label
    return "info"


def _magnitude_score(pct: float | None, threshold: float) -> float:
    """How far past the threshold, as a ratio (1.0 = exactly at threshold)."""
    if pct is None:
        return 1.0  # base-zero / undefined — give it a baseline magnitude
    ratio = abs(pct) / abs(threshold) if threshold != 0 else (1.0 if pct else 0.0)
    return max(ratio, 0.0)


# ──────────────────────────────────────────────────────────────────────────
# 3. Main analyzer
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class RootIQAnalyzer:
    """Reusable SME business data analyzer.

    Parameters
    ----------
    workbook_path : str
        Path to the Excel workbook.
    baseline_period : tuple[date, date]
        (start, end) inclusive.
    current_period : tuple[date, date]
        (start, end) inclusive.
    out_dir : str | None
        Directory for output files.  Defaults to the workbook's directory.
    """

    workbook_path: str
    baseline_period: tuple[date, date] = field(default_factory=lambda: BASELINE_PERIOD)
    current_period: tuple[date, date] = field(default_factory=lambda: CURRENT_PERIOD)
    out_dir: str | None = None

    # internal state
    _sheets: dict[str, pd.DataFrame] = field(default_factory=dict, init=False)
    _data_quality: dict[str, Any] = field(default_factory=dict, init=False)
    _metrics: list[dict] = field(default_factory=list, init=False)
    _anomalies: list[dict] = field(default_factory=list, init=False)

    # ── public API ────────────────────────────────────────────────────────

    def run(self) -> dict:
        """Execute the full pipeline and return the structured result dict."""
        self._load()
        self._validate_and_clean()
        self._tag_periods()
        self._compute_all_metrics()
        self._detect_anomalies()
        self._rank_anomalies()
        result = self._build_result()
        self._save(result)
        return result

    # ── 3a. Load ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        xls = pd.ExcelFile(self.workbook_path)
        for name in xls.sheet_names:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df = pd.read_excel(xls, sheet_name=name)
            # normalise column names: strip, lower
            df.columns = [str(c).strip() for c in df.columns]
            self._sheets[name] = df

    # ── 3b. Validate & clean ──────────────────────────────────────────────

    def _validate_and_clean(self) -> None:
        missing_values: list[dict] = []
        invalid_values: list[dict] = []
        warnings_list: list[dict] = []

        for sheet_name, df in self._sheets.items():
            if sheet_name not in EXPECTED_SHEETS:
                warnings_list.append({
                    "sheet": sheet_name,
                    "warning": f"Unexpected sheet '{sheet_name}' — loaded but "
                               f"not validated against a known schema.",
                })
                continue

            expected = EXPECTED_SHEETS[sheet_name]
            present = list(df.columns)
            missing_cols = [c for c in expected if c not in present]
            if missing_cols:
                msg = (f"Sheet '{sheet_name}' is missing required columns: "
                       f"{missing_cols}")
                warnings_list.append({"sheet": sheet_name, "warning": msg})

            # parse dates
            for col in DATE_COLUMNS.get(sheet_name, []):
                if col in df.columns:
                    parsed = df[col].apply(_to_date)
                    bad = parsed.isna() & df[col].notna()
                    if bad.any():
                        for idx in df[bad].index:
                            invalid_values.append({
                                "sheet": sheet_name,
                                "column": col,
                                "row": int(idx) + 2,
                                "value": str(df.loc[idx, col]),
                                "issue": "unparseable date",
                            })
                    df[col] = parsed

            # convert numerics
            for col in NUMERIC_COLUMNS.get(sheet_name, []):
                if col in df.columns:
                    converted = df[col].apply(_to_num_coerce)
                    bad = converted.isna() & df[col].notna()
                    if bad.any():
                        for idx in df[bad].index:
                            invalid_values.append({
                                "sheet": sheet_name,
                                "column": col,
                                "row": int(idx) + 2,
                                "value": str(df.loc[idx, col]),
                                "issue": "non-numeric value",
                            })
                    df[col] = converted

            # check missing values — exclude known sentinel columns
            # where "None" text in Excel becomes NaN in pandas
            sentinel_cols = {"Customer_Feedback": {"complaint_type"}}
            for col in df.columns:
                na_count = int(df[col].isna().sum())
                if na_count > 0:
                    is_sentinel = (sheet_name in sentinel_cols
                                   and col in sentinel_cols[sheet_name])
                    if is_sentinel:
                        warnings_list.append({
                            "sheet": sheet_name,
                            "warning": f"Column '{col}' has {na_count} NaN values "
                                       f"(originally 'None' in Excel, treated as "
                                       f"'no complaint').",
                        })
                    else:
                        missing_values.append({
                            "sheet": sheet_name,
                            "column": col,
                            "count": na_count,
                            "pct": round(na_count / len(df) * 100, 2) if len(df) else 0,
                        })

        # identity checks
        self._check_identities(warnings_list)

        self._data_quality = {
            "missing_values": missing_values,
            "invalid_values": invalid_values,
            "warnings": warnings_list,
        }

    def _check_identities(self, warnings_list: list[dict]) -> None:
        """Validate internal consistency identities (raise-level → warning)."""
        if "Sales" in self._sheets:
            df = self._sheets["Sales"]
            req = {"quantity", "unit_price", "revenue"}
            if req.issubset(df.columns):
                mism = df[(df["quantity"] * df["unit_price"]).round(4)
                          != df["revenue"].round(4)]
                if len(mism):
                    warnings_list.append({
                        "sheet": "Sales",
                        "warning": f"{len(mism)} rows where revenue != "
                                   f"quantity * unit_price",
                    })

        if "Inventory" in self._sheets:
            df = self._sheets["Inventory"]
            req = {"opening_stock", "received", "sold", "closing_stock"}
            if req.issubset(df.columns):
                mism = df[(df["opening_stock"] + df["received"] - df["sold"])
                          .round(4) != df["closing_stock"].round(4)]
                if len(mism):
                    warnings_list.append({
                        "sheet": "Inventory",
                        "warning": f"{len(mism)} rows where closing_stock != "
                                   f"opening_stock + received - sold",
                    })

        if "Purchase_Orders" in self._sheets:
            df = self._sheets["Purchase_Orders"]
            if {"request_date", "approval_date", "approval_days"}.issubset(df.columns):
                for _, r in df.iterrows():
                    if r["request_date"] and r["approval_date"]:
                        ad = (r["approval_date"] - r["request_date"]).days
                        if ad != r["approval_days"]:
                            warnings_list.append({
                                "sheet": "Purchase_Orders",
                                "warning": f"{r.get('po_id','?')}: approval_days "
                                           f"({r['approval_days']}) != "
                                           f"approval_date - request_date ({ad})",
                            })

    # ── 3c. Tag periods ───────────────────────────────────────────────────

    def _tag_periods(self) -> None:
        b0, b1 = self.baseline_period
        c0, c1 = self.current_period

        def tag(d):
            if d is None or (isinstance(d, float) and math.isnan(d)):
                return "UNKNOWN"
            if isinstance(d, datetime):
                d = d.date()
            if b0 <= d <= b1:
                return "BASELINE"
            if c0 <= d <= c1:
                return "CURRENT"
            return "OUTSIDE"

        for name, df in self._sheets.items():
            primary_date = {
                "Sales": "date",
                "Inventory": "date",
                "Customer_Feedback": "date",
                "Purchase_Orders": "request_date",
            }.get(name)
            if primary_date and primary_date in df.columns:
                df["_period"] = df[primary_date].apply(tag)

    # ── 3d. Compute metrics ───────────────────────────────────────────────

    def _compute_all_metrics(self) -> None:
        self._metrics = []
        if "Sales" in self._sheets:
            self._compute_sales_metrics()
        if "Inventory" in self._sheets:
            self._compute_inventory_metrics()
        if "Purchase_Orders" in self._sheets:
            self._compute_procurement_metrics()
        if "Suppliers" in self._sheets:
            self._compute_supplier_metrics()
        if "Customer_Feedback" in self._sheets:
            self._compute_customer_metrics()

    # ── Sales ─────────────────────────────────────────────────────────────

    def _compute_sales_metrics(self) -> None:
        df = self._sheets["Sales"]
        products = sorted(df["product_id"].dropna().unique())

        # overall
        b_rev = df.loc[df["_period"] == "BASELINE", "revenue"].sum()
        c_rev = df.loc[df["_period"] == "CURRENT", "revenue"].sum()
        pct, _ = _pct_change(b_rev, c_rev)
        self._add_metric("product", "ALL", "total_revenue", b_rev, c_rev, pct)

        b_qty = df.loc[df["_period"] == "BASELINE", "quantity"].sum()
        c_qty = df.loc[df["_period"] == "CURRENT", "quantity"].sum()
        pct_q, _ = _pct_change(b_qty, c_qty)
        self._add_metric("product", "ALL", "total_units_sold", b_qty, c_qty, pct_q)

        for p in products:
            sub = df[df["product_id"] == p]
            b = sub.loc[sub["_period"] == "BASELINE"]
            c = sub.loc[sub["_period"] == "CURRENT"]

            b_r, c_r = b["revenue"].sum(), c["revenue"].sum()
            pct_r, _ = _pct_change(b_r, c_r)
            self._add_metric("product", p, "revenue", b_r, c_r, pct_r)

            b_q, c_q = b["quantity"].sum(), c["quantity"].sum()
            pct_u, _ = _pct_change(b_q, c_q)
            self._add_metric("product", p, "units_sold", b_q, c_q, pct_u)

            b_p = b_r / b_q if b_q else None
            c_p = c_r / c_q if c_q else None
            pct_p, _ = _pct_change(b_p, c_p)
            self._add_metric("product", p, "avg_selling_price", b_p, c_p, pct_p)

            # contribution to total revenue change
            total_delta = c_rev - b_rev
            if total_delta != 0:
                contrib = (c_r - b_r) / total_delta * 100.0
            else:
                contrib = None
            self._add_metric("product", p, "revenue_contribution_pct",
                             None, None, contrib,
                             extra={"contribution_pct": contrib})

    # ── Inventory ─────────────────────────────────────────────────────────

    def _compute_inventory_metrics(self) -> None:
        df = self._sheets["Inventory"]
        products = sorted(df["product_id"].dropna().unique())

        for p in products:
            sub = df[df["product_id"] == p]
            b = sub.loc[sub["_period"] == "BASELINE"]
            c = sub.loc[sub["_period"] == "CURRENT"]

            b_sh = b["stockout_hours"].sum()
            c_sh = c["stockout_hours"].sum()
            pct_sh, bz = _pct_change(b_sh, c_sh)
            self._add_metric("product", p, "total_stockout_hours", b_sh, c_sh, pct_sh,
                             extra={"base_zero": bz})

            b_avg_sh = b_sh / PERIOD_DAYS
            c_avg_sh = c_sh / PERIOD_DAYS
            pct_ash, bz2 = _pct_change(b_avg_sh, c_avg_sh)
            self._add_metric("product", p, "avg_stockout_hours", b_avg_sh, c_avg_sh,
                             pct_ash, extra={"base_zero": bz2})

            b_sd = int((b["stockout_hours"] > 0).sum())
            c_sd = int((c["stockout_hours"] > 0).sum())
            pct_sd, bz3 = _pct_change(float(b_sd), float(c_sd))
            self._add_metric("product", p, "stockout_days", float(b_sd), float(c_sd),
                             pct_sd, extra={"base_zero": bz3})

            b_cs = b["closing_stock"].mean() if len(b) else None
            c_cs = c["closing_stock"].mean() if len(c) else None
            pct_cs, _ = _pct_change(b_cs, c_cs)
            self._add_metric("product", p, "avg_closing_stock", b_cs, c_cs, pct_cs)

            b_av = (1 - b_sh / (24 * PERIOD_DAYS)) * 100 if len(b) else None
            c_av = (1 - c_sh / (24 * PERIOD_DAYS)) * 100 if len(c) else None
            pp_av = _pp_change(b_av, c_av)
            self._add_metric("product", p, "availability_pct", b_av, c_av, None,
                             extra={"pp_change": pp_av})

    # ── Procurement ───────────────────────────────────────────────────────

    def _compute_procurement_metrics(self) -> None:
        df = self._sheets["Purchase_Orders"]
        if "_period" not in df.columns:
            return

        # join expected_lead_time from Suppliers
        if "Suppliers" in self._sheets:
            sup = self._sheets["Suppliers"]
            if "product_id" in sup.columns and "expected_lead_time_days" in sup.columns:
                exp_map = sup.set_index("product_id")["expected_lead_time_days"].to_dict()
                df["expected_lead_time"] = df["product_id"].map(exp_map)
                df["delay_days"] = df["supplier_lead_days"] - df["expected_lead_time"]

        b = df[df["_period"] == "BASELINE"]
        c = df[df["_period"] == "CURRENT"]

        # overall approval time
        b_appr = b["approval_days"].mean() if len(b) else None
        c_appr = c["approval_days"].mean() if len(c) else None
        pct_appr, _ = _pct_change(b_appr, c_appr)
        self._add_metric("procurement", "ALL", "avg_approval_time",
                         b_appr, c_appr, pct_appr)

        # overall supplier lead time
        b_lead = b["supplier_lead_days"].mean() if len(b) else None
        c_lead = c["supplier_lead_days"].mean() if len(c) else None
        pct_lead, _ = _pct_change(b_lead, c_lead)
        self._add_metric("procurement", "ALL", "avg_supplier_lead_time",
                         b_lead, c_lead, pct_lead)

        # fulfilment time = delivery - request (in days)
        if "request_date" in df.columns and "delivery_date" in df.columns:
            df["_fulfilment_days"] = df.apply(
                lambda r: (r["delivery_date"] - r["request_date"]).days
                if r["delivery_date"] and r["request_date"] else None, axis=1)
            b_ft = df.loc[df["_period"] == "BASELINE", "_fulfilment_days"].mean()
            c_ft = df.loc[df["_period"] == "CURRENT", "_fulfilment_days"].mean()
            pct_ft, _ = _pct_change(b_ft, c_ft)
            self._add_metric("procurement", "ALL", "avg_fulfilment_time",
                             b_ft, c_ft, pct_ft)

        # late orders
        if "delay_days" in df.columns:
            b_late = float((df.loc[df["_period"] == "BASELINE", "delay_days"] > 0).sum())
            c_late = float((df.loc[df["_period"] == "CURRENT", "delay_days"] > 0).sum())
            pct_late, bz_late = _pct_change(b_late, c_late)
            self._add_metric("procurement", "ALL", "late_orders_count",
                             b_late, c_late, pct_late,
                             extra={"base_zero": bz_late})

        # by product
        for p in sorted(df["product_id"].dropna().unique()):
            sub_b = b[b["product_id"] == p]
            sub_c = c[c["product_id"] == p]
            b_p_appr = sub_b["approval_days"].mean() if len(sub_b) else None
            c_p_appr = sub_c["approval_days"].mean() if len(sub_c) else None
            pct_p_appr, _ = _pct_change(b_p_appr, c_p_appr)
            self._add_metric("procurement", p, "approval_time_by_product",
                             b_p_appr, c_p_appr, pct_p_appr)

    # ── Suppliers ─────────────────────────────────────────────────────────

    def _compute_supplier_metrics(self) -> None:
        df = self._sheets["Suppliers"]
        if df.empty:
            return

        # PO-derived lead time by supplier (period-split)
        po = self._sheets.get("Purchase_Orders")
        po_by_sup = {}
        if po is not None and "_period" in po.columns:
            for sid in df["supplier_id"].unique():
                b = po[(po["supplier_id"] == sid) & (po["_period"] == "BASELINE")]
                c = po[(po["supplier_id"] == sid) & (po["_period"] == "CURRENT")]
                po_by_sup[sid] = {
                    "b_lead": b["supplier_lead_days"].mean() if len(b) else None,
                    "c_lead": c["supplier_lead_days"].mean() if len(c) else None,
                }

        for _, r in df.iterrows():
            sid = r["supplier_id"]
            b_lt = r.get("baseline_avg_lead_days")
            c_lt = r.get("current_avg_lead_days")
            pct_lt, _ = _pct_change(_safe_num(b_lt), _safe_num(c_lt))
            self._add_metric("supplier", sid, "lead_time_change",
                             _safe_num(b_lt), _safe_num(c_lt), pct_lt)

            b_uc = _safe_num(r.get("baseline_unit_cost"))
            c_uc = _safe_num(r.get("current_unit_cost"))
            pct_uc, _ = _pct_change(b_uc, c_uc)
            self._add_metric("supplier", sid, "unit_cost_change",
                             b_uc, c_uc, pct_uc)

            otd = _safe_num(r.get("on_time_delivery_rate_pct"))
            self._add_metric("supplier", sid, "otd_reported_pct",
                             None, otd, None,
                             extra={"no_period_split": True})

            # derived OTD
            if sid in po_by_sup:
                b_d = po_by_sup[sid]["b_lead"]
                c_d = po_by_sup[sid]["c_lead"]
                # compute from PO data
                po_b = po[(po["supplier_id"] == sid) & (po["_period"] == "BASELINE")]
                po_c = po[(po["supplier_id"] == sid) & (po["_period"] == "CURRENT")]
                exp = _safe_num(r.get("expected_lead_time_days"))
                if exp is not None:
                    b_otd = (po_b["supplier_lead_days"] <= exp).mean() * 100 if len(po_b) else None
                    c_otd = (po_c["supplier_lead_days"] <= exp).mean() * 100 if len(po_c) else None
                    pp_otd = _pp_change(b_otd, c_otd)
                    self._add_metric("supplier", sid, "otd_derived_pct",
                                     b_otd, c_otd, None,
                                     extra={"pp_change": pp_otd})

    # ── Customer ──────────────────────────────────────────────────────────

    def _compute_customer_metrics(self) -> None:
        df = self._sheets["Customer_Feedback"]
        if "_period" not in df.columns:
            return

        b = df[df["_period"] == "BASELINE"]
        c = df[df["_period"] == "CURRENT"]
        b_n, c_n = len(b), len(c)

        # complaint count — treat NaN / "None" / empty as "no complaint"
        def _is_complaint(val):
            if pd.isna(val):
                return False
            s = str(val).strip()
            return s not in ("None", "", "nan", "NaT")

        b_comp = int(b["complaint_type"].apply(_is_complaint).sum())
        c_comp = int(c["complaint_type"].apply(_is_complaint).sum())
        pct_comp, _ = _pct_change(float(b_comp), float(c_comp))
        self._add_metric("customer", "ALL", "complaint_count",
                         float(b_comp), float(c_comp), pct_comp)

        # complaint rate
        b_rate = b_comp / b_n * 100 if b_n else None
        c_rate = c_comp / c_n * 100 if c_n else None
        pct_rate, bz_rate = _pct_change(b_rate, c_rate)
        self._add_metric("customer", "ALL", "complaint_rate_pct",
                         b_rate, c_rate, pct_rate,
                         extra={"base_zero": bz_rate,
                                "pp_change": _pp_change(b_rate, c_rate)})

        # refund rate
        b_ref = int((b["refund"].astype(str).str.strip() == "Yes").sum())
        c_ref = int((c["refund"].astype(str).str.strip() == "Yes").sum())
        b_ref_r = b_ref / b_n * 100 if b_n else None
        c_ref_r = c_ref / c_n * 100 if c_n else None
        pct_ref, bz_ref = _pct_change(b_ref_r, c_ref_r)
        self._add_metric("customer", "ALL", "refund_rate_pct",
                         b_ref_r, c_ref_r, pct_ref,
                         extra={"base_zero": bz_ref,
                                "pp_change": _pp_change(b_ref_r, c_ref_r)})

        # cancellation rate
        b_can = int((b["order_cancelled"].astype(str).str.strip() == "Yes").sum())
        c_can = int((c["order_cancelled"].astype(str).str.strip() == "Yes").sum())
        b_can_r = b_can / b_n * 100 if b_n else None
        c_can_r = c_can / c_n * 100 if c_n else None
        pct_can, bz_can = _pct_change(b_can_r, c_can_r)
        self._add_metric("customer", "ALL", "cancellation_rate_pct",
                         b_can_r, c_can_r, pct_can,
                         extra={"base_zero": bz_can,
                                "pp_change": _pp_change(b_can_r, c_can_r)})

        # avg rating
        b_rt = b["rating"].mean() if b_n else None
        c_rt = c["rating"].mean() if c_n else None
        pct_rt, _ = _pct_change(b_rt, c_rt)
        self._add_metric("customer", "ALL", "avg_rating",
                         b_rt, c_rt, pct_rt)

        # complaint-type breakdown
        def _complaint_val(val):
            if pd.isna(val):
                return None
            s = str(val).strip()
            if s in ("None", "", "nan", "NaT"):
                return None
            return s

        b_types = b["complaint_type"].apply(_complaint_val).dropna()
        c_types = c["complaint_type"].apply(_complaint_val).dropna()
        all_types = sorted(set(b_types.unique()) | set(c_types.unique()))
        for t in all_types:
            b_t = int((b_types == t).sum())
            c_t = int((c_types == t).sum())
            b_share = b_t / b_comp * 100 if b_comp else 0.0
            c_share = c_t / c_comp * 100 if c_comp else 0.0
            self._add_metric("customer", "ALL", f"complaint_type:{t}",
                             float(b_t), float(c_t),
                             None,
                             extra={"share_baseline_pct": b_share,
                                    "share_current_pct": c_share,
                                    "share_pp_change": c_share - b_share})

    # ── 3e. Anomaly detection ─────────────────────────────────────────────

    def _detect_anomalies(self) -> None:
        """Apply user-specified anomaly rules to the computed metrics."""
        self._anomalies = []
        for m in self._metrics:
            self._check_rule(m)

    def _check_rule(self, m: dict) -> None:
        metric_name = m["metric"]
        area = m["area"]
        ident = m["identifier"]
        base = m["baseline"]
        cur = m["current"]
        pct = m["change_pct"]
        extra = m.get("extra", {})

        # Rule: revenue (overall)
        if metric_name == "total_revenue" and area == "product" and ident == "ALL":
            if pct is not None and pct <= ANOMALY_RULES["revenue"]["threshold"]:
                self._add_anomaly("revenue", "overall", base, cur, pct,
                                  ANOMALY_RULES["revenue"], "Sales.revenue")

        # Rule: product revenue
        if metric_name == "revenue" and area == "product" and ident != "ALL":
            if pct is not None and pct <= ANOMALY_RULES["product_revenue"]["threshold"]:
                self._add_anomaly("product_revenue", ident, base, cur, pct,
                                  ANOMALY_RULES["product_revenue"], "Sales.revenue")

        # Rule: stockout hours
        if metric_name == "total_stockout_hours":
            rule = ANOMALY_RULES["stockout_hours"]
            flagged = False
            if base is not None and cur is not None:
                if base > 0 and cur >= rule["threshold_mult"] * base:
                    flagged = True
                if base == 0 and cur > rule["threshold_abs"]:
                    flagged = True
            if flagged:
                self._add_anomaly("stockout_hours", ident, base, cur, pct,
                                  rule, "Inventory.stockout_hours")

        # Rule: PO approval time
        if metric_name == "avg_approval_time":
            rule = ANOMALY_RULES["po_approval_time"]
            flagged = False
            if cur is not None and cur > rule["threshold_abs"]:
                flagged = True
            if pct is not None and pct > 0 and (cur is not None and base is not None
                                                and cur > rule["threshold_mult"] * base):
                flagged = True
            if flagged:
                self._add_anomaly("po_approval_time", "overall", base, cur, pct,
                                  rule, "Purchase_Orders.approval_days")

        # Rule: supplier lead time
        if metric_name == "lead_time_change":
            rule = ANOMALY_RULES["supplier_lead_time"]
            if pct is not None and pct > 0 and base and cur and cur > rule["threshold"] * base:
                self._add_anomaly("supplier_lead_time", ident, base, cur, pct,
                                  rule, "Suppliers.current_avg_lead_days")

        # Rule: unit cost
        if metric_name == "unit_cost_change":
            rule = ANOMALY_RULES["unit_cost"]
            if pct is not None and pct >= rule["threshold"]:
                self._add_anomaly("unit_cost", ident, base, cur, pct,
                                  rule, "Suppliers.current_unit_cost")

        # Rule: complaint rate
        if metric_name == "complaint_rate_pct":
            rule = ANOMALY_RULES["complaint_rate"]
            pp = extra.get("pp_change")
            # Use relative change (pct) as primary; fall back to pp for base-zero
            if pct is not None and pct >= rule["threshold"]:
                self._add_anomaly("complaint_rate", "overall", base, cur, pct,
                                  rule, "Customer_Feedback.complaint_type")
            elif extra.get("base_zero") and pp is not None and pp > 0:
                self._add_anomaly("complaint_rate", "overall", base, cur, pct,
                                  rule, "Customer_Feedback.complaint_type",
                                  flags=["base_zero"])

        # Rule: refund rate
        if metric_name == "refund_rate_pct":
            rule = ANOMALY_RULES["refund_rate"]
            pp = extra.get("pp_change")
            if pct is not None and pct >= rule["threshold"]:
                self._add_anomaly("refund_rate", "overall", base, cur, pct,
                                  rule, "Customer_Feedback.refund")
            elif extra.get("base_zero") and pp is not None and pp > 0:
                self._add_anomaly("refund_rate", "overall", base, cur, pct,
                                  rule, "Customer_Feedback.refund",
                                  flags=["base_zero"])

        # Rule: fulfilment time
        if metric_name == "avg_fulfilment_time":
            rule = ANOMALY_RULES["fulfilment_time"]
            if pct is not None and pct >= rule["threshold"]:
                self._add_anomaly("fulfilment_time", "overall", base, cur, pct,
                                  rule, "Purchase_Orders.delivery_date - request_date")

        # Rule: late orders
        if metric_name == "late_orders_count":
            rule = ANOMALY_RULES["late_orders"]
            pp = (cur - base) if (base is not None and cur is not None) else None
            if pct is not None and pct >= rule["threshold"]:
                self._add_anomaly("late_orders", "overall", base, cur, pct,
                                  rule, "Purchase_Orders.delay_days")
            elif extra.get("base_zero") and pp is not None and pp > 0:
                self._add_anomaly("late_orders", "overall", base, cur, pct,
                                  rule, "Purchase_Orders.delay_days",
                                  flags=["base_zero"])

    def _add_anomaly(self, rule_key: str, area: str, base, cur, pct,
                     rule: dict, evidence: str, flags: list = None) -> None:
        rel = rule["relevance"]
        threshold = rule.get("threshold", rule.get("threshold_abs", 0))
        mag = _magnitude_score(pct, threshold) if threshold else 1.0
        score = mag * rel * 10  # scale to 0-100ish
        severity = _severity(score)
        self._anomalies.append({
            "metric": rule["label"],
            "affected_area": area,
            "baseline": _round(base),
            "current": _round(cur),
            "change_pct": _round(pct),
            "severity": severity,
            "evidence_source": evidence,
            "score": round(score, 2),
            "flags": flags or [],
        })

    # ── 3f. Rank anomalies ────────────────────────────────────────────────

    def _rank_anomalies(self) -> None:
        self._anomalies.sort(key=lambda a: (-a["score"], a["metric"]))

    # ── 3g. Build result ──────────────────────────────────────────────────

    def _add_metric(self, area: str, identifier: str, metric: str,
                    baseline, current, change_pct, extra: dict = None) -> None:
        sev = self._metric_severity(area, identifier, metric, change_pct, extra or {})
        self._metrics.append({
            "area": area,
            "identifier": identifier,
            "metric": metric,
            "baseline": _round(baseline),
            "current": _round(current),
            "change_pct": _round(change_pct),
            "severity": sev,
            "extra": extra or {},
        })

    @staticmethod
    def _metric_severity(area, ident, metric, pct, extra) -> str:
        """Lightweight severity for non-anomaly metrics (for the metric arrays)."""
        if pct is None:
            if extra.get("base_zero"):
                return "watch"
            return "info"
        if metric == "total_revenue" and pct <= -10:
            return "high"
        if metric == "revenue" and pct <= -15:
            return "high"
        if abs(pct) >= 50:
            return "high" if pct < 0 else "medium"
        if abs(pct) >= 20:
            return "medium" if pct < 0 else "low"
        return "low"

    def _build_result(self) -> dict:
        # business summary
        sales = self._sheets.get("Sales")
        if sales is not None and "_period" in sales.columns:
            b_rev = sales.loc[sales["_period"] == "BASELINE", "revenue"].sum()
            c_rev = sales.loc[sales["_period"] == "CURRENT", "revenue"].sum()
            pct, _ = _pct_change(b_rev, c_rev)
        else:
            b_rev = c_rev = pct = None

        b0, b1 = self.baseline_period
        c0, c1 = self.current_period

        # partition metrics by area
        product_metrics = []
        procurement_metrics = []
        supplier_metrics = []
        customer_metrics = []

        for m in self._metrics:
            entry = {
                ("product_id" if m["area"] == "product"
                 else "supplier_id" if m["area"] == "supplier"
                 else "scope"): m["identifier"],
                "metric": m["metric"],
                "baseline": m["baseline"],
                "current": m["current"],
                "change_pct": m["change_pct"],
                "severity": m["severity"],
            }
            # add extra fields inline
            for k, v in m.get("extra", {}).items():
                if k not in entry:
                    entry[k] = _round(v) if isinstance(v, (int, float)) else v

            if m["area"] == "product":
                product_metrics.append(entry)
            elif m["area"] == "procurement":
                procurement_metrics.append(entry)
            elif m["area"] == "supplier":
                supplier_metrics.append(entry)
            elif m["area"] == "customer":
                customer_metrics.append(entry)

        # strip internal score/flags from the public anomaly list
        anomalies_out = []
        for a in self._anomalies:
            anomalies_out.append({
                "metric": a["metric"],
                "affected_area": a["affected_area"],
                "baseline": a["baseline"],
                "current": a["current"],
                "change_pct": a["change_pct"],
                "severity": a["severity"],
                "evidence_source": a["evidence_source"],
            })

        return {
            "business_summary": {
                "baseline_period": f"{b0.isoformat()} to {b1.isoformat()}",
                "current_period": f"{c0.isoformat()} to {c1.isoformat()}",
                "overall_revenue_baseline": _round(b_rev),
                "overall_revenue_current": _round(c_rev),
                "overall_revenue_change_pct": _round(pct),
            },
            "product_metrics": product_metrics,
            "procurement_metrics": procurement_metrics,
            "supplier_metrics": supplier_metrics,
            "customer_metrics": customer_metrics,
            "anomalies": anomalies_out,
            "data_quality": self._data_quality,
        }

    # ── 3h. Save ──────────────────────────────────────────────────────────

    def _save(self, result: dict) -> None:
        out_dir = self.out_dir or os.path.dirname(os.path.abspath(self.workbook_path))
        os.makedirs(out_dir, exist_ok=True)

        json_path = os.path.join(out_dir, "analysis_summary.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        csv_path = os.path.join(out_dir, "analysis_summary.csv")
        rows = []
        for section in ("product_metrics", "procurement_metrics",
                        "supplier_metrics", "customer_metrics"):
            for entry in result[section]:
                ident_key = ("product_id" if "product_id" in entry
                             else "supplier_id" if "supplier_id" in entry
                             else "scope")
                row = {
                    "category": section.replace("_metrics", ""),
                    "identifier": entry.get(ident_key, ""),
                    "metric": entry["metric"],
                    "baseline": entry["baseline"],
                    "current": entry["current"],
                    "change_pct": entry["change_pct"],
                    "severity": entry["severity"],
                }
                rows.append(row)
        # add anomalies
        for a in result["anomalies"]:
            rows.append({
                "category": "anomaly",
                "identifier": a["affected_area"],
                "metric": a["metric"],
                "baseline": a["baseline"],
                "current": a["current"],
                "change_pct": a["change_pct"],
                "severity": a["severity"],
            })
        pd.DataFrame(rows).to_csv(csv_path, index=False)


# ──────────────────────────────────────────────────────────────────────────
# 4. Numeric coercion helper (module-level for pandas .apply)
# ──────────────────────────────────────────────────────────────────────────

def _to_num_coerce(val: Any) -> float | None:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    try:
        return float(str(val).strip())
    except (ValueError, TypeError):
        return None


# ──────────────────────────────────────────────────────────────────────────
# 5. CLI
# ──────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="RootIQ SME Business Data Analyzer")
    parser.add_argument("workbook", help="Path to the Excel workbook")
    parser.add_argument("--out-dir", default=None,
                        help="Output directory (default: workbook directory)")
    args = parser.parse_args()

    analyzer = RootIQAnalyzer(
        workbook_path=args.workbook,
        out_dir=args.out_dir,
    )
    result = analyzer.run()

    n_anom = len(result["anomalies"])
    n_prod = len(result["product_metrics"])
    n_proc = len(result["procurement_metrics"])
    n_sup = len(result["supplier_metrics"])
    n_cust = len(result["customer_metrics"])
    rev_b = result["business_summary"]["overall_revenue_baseline"]
    rev_c = result["business_summary"]["overall_revenue_current"]
    rev_pct = result["business_summary"]["overall_revenue_change_pct"]

    print(f"Done.  Revenue {rev_b} -> {rev_c} ({rev_pct}%)")
    print(f"Metrics: product={n_prod}  procurement={n_proc}  "
          f"supplier={n_sup}  customer={n_cust}")
    print(f"Anomalies detected: {n_anom}")
    for a in result["anomalies"]:
        print(f"  [{a['severity']}] {a['metric']} — {a['affected_area']} "
              f"({a['baseline']} -> {a['current']}, {a['change_pct']}%)")
    out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.workbook))
    print(f"Files saved: {os.path.join(out_dir, 'analysis_summary.json')}")
    print(f"           {os.path.join(out_dir, 'analysis_summary.csv')}")


if __name__ == "__main__":
    main()
