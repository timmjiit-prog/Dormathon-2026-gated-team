"""
RootIQ — deterministic metric engine (reference implementation of RootIQ_Calculation_Spec.md v1.0).

Reads the source workbook, validates data-quality identities, tags periods, computes
M01-M28 and emits one flat record per metric.

No imputation. No outlier removal. No LLM estimation. Pure arithmetic.

Usage:
    python rootiq_metrics.py <workbook.xlsx> [out.json]
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from typing import Any

import openpyxl

# --------------------------------------------------------------------------
# 0. Configuration (spec section 0)
# --------------------------------------------------------------------------

BASELINE = (dt.date(2026, 8, 3), dt.date(2026, 8, 30))
CURRENT = (dt.date(2026, 8, 31), dt.date(2026, 9, 27))
PERIOD_DAYS = 28

TH = {
    "REVENUE_PCT": 10.0,
    "CONTRIB_DOMINANT": 50.0,
    "STOCKOUT_DAYS": 1,
    "AVAILABILITY_PP": -2.0,
    "CLOSING_STOCK_PCT": -25.0,
    "APPROVAL_DELTA_DAYS": 1.0,
    "APPROVAL_PCT": 100.0,
    "LEAD_DELTA_DAYS": 0.0,
    "DELAY_ABNORMAL_DAYS": 2,
    "OTD_MIN_PCT": 90.0,
    "COMPLAINT_RATE_PP": 5.0,
    "RATING_DELTA": -0.25,
    "COMPLAINT_TYPE_PP": 20.0,
}

SHEETS = ["Sales", "Inventory", "Purchase_Orders", "Suppliers", "Customer_Feedback"]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def to_date(v: Any) -> dt.date:
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    return dt.date.fromisoformat(str(v)[:10])


def period_of(d: dt.date) -> str:
    if BASELINE[0] <= d <= BASELINE[1]:
        return "BASELINE"
    if CURRENT[0] <= d <= CURRENT[1]:
        return "CURRENT"
    return "OUTSIDE"


def pct_change(base: float | None, cur: float | None) -> tuple[float | None, list[str]]:
    """Relative change. Returns (None, ['base_zero']) when base is 0 or absent."""
    if base is None or cur is None:
        return None, ["no_rows"]
    if base == 0:
        return None, ["base_zero"]
    return (cur - base) / base * 100.0, []


def ols_slope(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else 0.0


def rec(metric_id, name, base, cur, delta=None, pct=None, pp=None,
        is_anomaly=False, threshold=None, flags=None, group=None):
    return {
        "metric_id": metric_id,
        "metric_name": name,
        "group": group or {"period": None, "product_id": None, "supplier_id": None},
        "value_baseline": base,
        "value_current": cur,
        "delta": delta,
        "pct_change": None if pct is None else round(pct, 4),
        "pp_change": None if pp is None else round(pp, 4),
        "is_anomaly": is_anomaly,
        "threshold_used": threshold,
        "flags": flags or [],
    }


# --------------------------------------------------------------------------
# load + validate
# --------------------------------------------------------------------------

def load(path: str) -> dict[str, list[dict]]:
    wb = openpyxl.load_workbook(path, data_only=True)
    out = {}
    for name in SHEETS:
        ws = wb[name]
        rows = list(ws.iter_rows(values_only=True))
        headers = [str(h) for h in rows[0]]
        data = []
        for r in rows[1:]:
            if all(c is None for c in r):
                continue
            data.append(dict(zip(headers, r)))
        out[name] = data
    return out


def validate(D: dict[str, list[dict]]) -> list[str]:
    """Data-quality identities. A failure must raise, not warn (spec 8.3.6)."""
    errors = []
    for r in D["Sales"]:
        if abs(r["revenue"] - r["quantity"] * r["unit_price"]) > 1e-9:
            errors.append(f"Sales {r['order_id']}: revenue != quantity * unit_price")
    for r in D["Inventory"]:
        if r["closing_stock"] != r["opening_stock"] + r["received"] - r["sold"]:
            errors.append(f"Inventory {r['date']}/{r['product_id']}: stock identity violated")
    for r in D["Purchase_Orders"]:
        ad = (to_date(r["approval_date"]) - to_date(r["request_date"])).days
        ld = (to_date(r["delivery_date"]) - to_date(r["order_date"])).days
        if ad != r["approval_days"]:
            errors.append(f"{r['po_id']}: approval_days mismatch")
        if ld != r["supplier_lead_days"]:
            errors.append(f"{r['po_id']}: supplier_lead_days mismatch")
        seq = [to_date(r[c]) for c in ("request_date", "approval_date", "order_date", "delivery_date")]
        if seq != sorted(seq):
            errors.append(f"{r['po_id']}: date order violated")
    if errors:
        raise AssertionError("Data-quality identity failure:\n  " + "\n  ".join(errors))
    return errors


# --------------------------------------------------------------------------
# metrics
# --------------------------------------------------------------------------

def compute(D: dict[str, list[dict]]) -> list[dict]:
    M: list[dict] = []
    sales, inv, po, sup_rows, fb = (D["Sales"], D["Inventory"], D["Purchase_Orders"],
                                    D["Suppliers"], D["Customer_Feedback"])
    prods = sorted({r["product_id"] for r in sales})
    pname = {r["product_id"]: r["product_name"] for r in sales}
    p2sup = {r["product_id"]: r for r in sup_rows}

    for r in sales:
        r["_p"] = period_of(to_date(r["date"]))
    for r in inv:
        r["_p"] = period_of(to_date(r["date"]))
        r["_di"] = (to_date(r["date"]) - BASELINE[0]).days
    for r in fb:
        r["_p"] = period_of(to_date(r["date"]))
    for r in po:
        r["_p"] = period_of(to_date(r["request_date"]))
        r["_exp"] = p2sup[r["product_id"]]["expected_lead_time_days"]
        r["_delay"] = r["supplier_lead_days"] - r["_exp"]

    # ---- SALES ----
    def sagg(period, p=None):
        sel = [r for r in sales if r["_p"] == period and (p is None or r["product_id"] == p)]
        q = sum(r["quantity"] for r in sel)
        rev = sum(r["revenue"] for r in sel)
        return {"orders": len(sel), "quantity": q, "revenue": rev,
                "avg_price": (rev / q if q else None)}

    tb, tc = sagg("BASELINE"), sagg("CURRENT")
    pct_rev, f_rev = pct_change(tb["revenue"], tc["revenue"])
    M.append(rec("M01", "total_revenue", tb["revenue"], tc["revenue"],
                 tc["revenue"] - tb["revenue"], pct_rev,
                 is_anomaly=bool(pct_rev is not None and abs(pct_rev) >= TH["REVENUE_PCT"]),
                 threshold=TH["REVENUE_PCT"], flags=f_rev))
    M.append(rec("M02", "revenue_pct_change", tb["revenue"], tc["revenue"],
                 tc["revenue"] - tb["revenue"], pct_rev,
                 is_anomaly=bool(pct_rev is not None and abs(pct_rev) >= TH["REVENUE_PCT"]) or bool(f_rev),
                 threshold=TH["REVENUE_PCT"], flags=f_rev))

    bp = {p: sagg("BASELINE", p) for p in prods}
    cp = {p: sagg("CURRENT", p) for p in prods}
    total_delta = tc["revenue"] - tb["revenue"]

    for p in prods:
        g = {"period": None, "product_id": p, "supplier_id": None}
        pctp, fp = pct_change(bp[p]["revenue"], cp[p]["revenue"])
        M.append(rec("M03", "revenue_by_product", bp[p]["revenue"], cp[p]["revenue"],
                     cp[p]["revenue"] - bp[p]["revenue"], pctp,
                     is_anomaly=bool(pctp is not None and abs(pctp) >= TH["REVENUE_PCT"]),
                     threshold=TH["REVENUE_PCT"], flags=fp, group=g))
        M.append(rec("M04", "revenue_pct_change_by_product", bp[p]["revenue"], cp[p]["revenue"],
                     cp[p]["revenue"] - bp[p]["revenue"], pctp,
                     is_anomaly=bool(pctp is not None and abs(pctp) >= TH["REVENUE_PCT"]),
                     threshold=TH["REVENUE_PCT"], flags=fp, group=g))
        pctq, fq = pct_change(bp[p]["quantity"], cp[p]["quantity"])
        M.append(rec("M05", "units_sold_by_product", bp[p]["quantity"], cp[p]["quantity"],
                     cp[p]["quantity"] - bp[p]["quantity"], pctq,
                     is_anomaly=bool(pctq is not None and abs(pctq) >= TH["REVENUE_PCT"]),
                     threshold=TH["REVENUE_PCT"], flags=fq, group=g))
        M.append(rec("M06", "units_sold_pct_change", bp[p]["quantity"], cp[p]["quantity"],
                     cp[p]["quantity"] - bp[p]["quantity"], pctq,
                     is_anomaly=bool(pctq is not None and abs(pctq) >= TH["REVENUE_PCT"]),
                     threshold=TH["REVENUE_PCT"], flags=fq, group=g))
        pctpr, fpr = pct_change(bp[p]["avg_price"], cp[p]["avg_price"])
        M.append(rec("M07a", "unit_price_per_product", bp[p]["avg_price"], cp[p]["avg_price"],
                     (cp[p]["avg_price"] - bp[p]["avg_price"]), pctpr,
                     is_anomaly=bool(cp[p]["avg_price"] != bp[p]["avg_price"]),
                     threshold=0.0, flags=fpr, group=g))
        contrib = (cp[p]["revenue"] - bp[p]["revenue"]) / total_delta * 100.0 if total_delta else None
        M.append(rec("M08", "contribution_to_revenue_decline", None, None, None, None, pp=None,
                     is_anomaly=bool(contrib is not None and abs(contrib) >= TH["CONTRIB_DOMINANT"]
                                     and (cp[p]["revenue"] - bp[p]["revenue"]) * total_delta > 0),
                     threshold=TH["CONTRIB_DOMINANT"],
                     flags=([] if total_delta else ["zero_total_change"]),
                     group=g) | {"contribution_pct": None if contrib is None else round(contrib, 4)})

    pctq_t, fq_t = pct_change(tb["quantity"], tc["quantity"])
    M.append(rec("M06", "units_sold_pct_change_total", tb["quantity"], tc["quantity"],
                 tc["quantity"] - tb["quantity"], pctq_t,
                 is_anomaly=bool(pctq_t is not None and abs(pctq_t) >= TH["REVENUE_PCT"]),
                 threshold=TH["REVENUE_PCT"], flags=fq_t))

    bp_all = tb["revenue"] / tb["quantity"]
    cp_all = tc["revenue"] / tc["quantity"]
    pct_ba, f_ba = pct_change(bp_all, cp_all)
    M.append(rec("M07b", "blended_avg_price", bp_all, cp_all, cp_all - bp_all, pct_ba,
                 is_anomaly=bool(pct_ba is not None and abs(pct_ba) >= TH["REVENUE_PCT"]),
                 threshold=TH["REVENUE_PCT"], flags=f_ba + ["mix_affected"]))

    rank = sorted(prods, key=lambda p: (cp[p]["revenue"] - bp[p]["revenue"], p))
    for i, p in enumerate(rank, 1):
        dlt = cp[p]["revenue"] - bp[p]["revenue"]
        M.append(rec("M09", "ranking_by_negative_revenue_impact", None, None, dlt, None,
                     is_anomaly=bool(i == 1 and dlt < 0 and total_delta
                                     and abs(dlt) >= 0.25 * abs(total_delta)),
                     threshold=25.0,
                     group={"period": None, "product_id": p, "supplier_id": None}) | {"rank": i})

    # ---- INVENTORY ----
    for p in prods:
        g = {"period": None, "product_id": p, "supplier_id": None}
        agg = {}
        for period in ("BASELINE", "CURRENT"):
            sel = [r for r in inv if r["product_id"] == p and r["_p"] == period]
            sh = [r["stockout_hours"] for r in sel]
            cs = [r["closing_stock"] for r in sel]
            agg[period] = {
                "total_sh": sum(sh),
                "avg_sh": sum(sh) / PERIOD_DAYS,
                "stockout_days": sum(1 for v in sh if v > 0),
                "zero_stock_days": sum(1 for v in cs if v == 0),
                "avg_cs": sum(cs) / PERIOD_DAYS,
                "min_cs": min(cs), "max_cs": max(cs),
                "slope": ols_slope([r["_di"] for r in sel], cs),
                "avail": (1 - sum(sh) / (24 * PERIOD_DAYS)) * 100.0,
            }
        b, c = agg["BASELINE"], agg["CURRENT"]

        def new_occ(bb, cc, mid, name, unit):
            pctv, fl = pct_change(bb, cc)
            M.append(rec(mid, name, bb, cc, cc - bb, pctv,
                         is_anomaly=bool((bb == 0 and cc > 0) or (pctv is not None and pctv >= 50)),
                         threshold=50.0, flags=fl, group=g))
        new_occ(b["total_sh"], c["total_sh"], "M10", "total_stockout_hours", "h")
        new_occ(b["avg_sh"], c["avg_sh"], "M11", "avg_stockout_hours", "h")
        pctd, fd = pct_change(b["stockout_days"], c["stockout_days"])
        M.append(rec("M12", "stockout_days", b["stockout_days"], c["stockout_days"],
                     c["stockout_days"] - b["stockout_days"], pctd,
                     is_anomaly=bool(c["stockout_days"] >= TH["STOCKOUT_DAYS"]),
                     threshold=TH["STOCKOUT_DAYS"], flags=fd, group=g))
        pctc, fc = pct_change(b["avg_cs"], c["avg_cs"])
        M.append(rec("M13", "closing_stock_trend_avg", b["avg_cs"], c["avg_cs"],
                     c["avg_cs"] - b["avg_cs"], pctc,
                     is_anomaly=bool((pctc is not None and pctc <= TH["CLOSING_STOCK_PCT"])
                                     or c["min_cs"] == 0
                                     or (b["slope"] > 0 > c["slope"])),
                     threshold=TH["CLOSING_STOCK_PCT"], flags=fc, group=g)
                 | {"slope_baseline": round(b["slope"], 4), "slope_current": round(c["slope"], 4),
                    "min_baseline": b["min_cs"], "min_current": c["min_cs"]})
        M.append(rec("M14", "availability_pct", b["avail"], c["avail"], None, None,
                     pp=c["avail"] - b["avail"],
                     is_anomaly=bool((c["avail"] - b["avail"]) <= TH["AVAILABILITY_PP"]),
                     threshold=TH["AVAILABILITY_PP"], group=g)
                 | {"availability_days_pct_baseline": (1 - b["stockout_days"] / PERIOD_DAYS) * 100,
                    "availability_days_pct_current": (1 - c["stockout_days"] / PERIOD_DAYS) * 100})

    # ---- PROCUREMENT ----
    psum = {}
    for period in ("BASELINE", "CURRENT"):
        sel = [r for r in po if r["_p"] == period]
        psum[period] = {
            "n": len(sel),
            "avg_appr": sum(r["approval_days"] for r in sel) / len(sel),
            "max_appr": max(r["approval_days"] for r in sel),
            "avg_lead": sum(r["supplier_lead_days"] for r in sel) / len(sel),
            "avg_delay": sum(r["_delay"] for r in sel) / len(sel),
            "delayed": sum(1 for r in sel if r["_delay"] > 0),
        }
    b, c = psum["BASELINE"], psum["CURRENT"]
    pcta, fa = pct_change(b["avg_appr"], c["avg_appr"])
    M.append(rec("M15", "avg_po_approval_time", b["avg_appr"], c["avg_appr"],
                 c["avg_appr"] - b["avg_appr"], pcta,
                 is_anomaly=bool((c["avg_appr"] - b["avg_appr"]) >= TH["APPROVAL_DELTA_DAYS"]
                                 or (pcta is not None and pcta >= TH["APPROVAL_PCT"])),
                 threshold=TH["APPROVAL_DELTA_DAYS"], flags=fa)
             | {"max_approval_days_baseline": b["max_appr"], "max_approval_days_current": c["max_appr"]})

    for p in prods:
        g = {"period": None, "product_id": p, "supplier_id": None}
        sub = {}
        for period in ("BASELINE", "CURRENT"):
            sel = [r for r in po if r["_p"] == period and r["product_id"] == p]
            sub[period] = (sum(r["approval_days"] for r in sel) / len(sel) if sel else None)
        pctp, fp = pct_change(sub["BASELINE"], sub["CURRENT"])
        fl = list(fp) + (["small_base"] if (sub["BASELINE"] is not None and sub["BASELINE"] < 0.5) else [])
        M.append(rec("M16", "po_approval_time_by_product", sub["BASELINE"], sub["CURRENT"],
                     (sub["CURRENT"] - sub["BASELINE"]) if None not in (sub["BASELINE"], sub["CURRENT"]) else None,
                     pctp,
                     is_anomaly=bool(None not in (sub["BASELINE"], sub["CURRENT"])
                                     and (sub["CURRENT"] - sub["BASELINE"]) >= TH["APPROVAL_DELTA_DAYS"]),
                     threshold=TH["APPROVAL_DELTA_DAYS"], flags=fl, group=g))

    pctl, fl_ = pct_change(b["avg_lead"], c["avg_lead"])
    M.append(rec("M17", "avg_supplier_lead_time", b["avg_lead"], c["avg_lead"],
                 c["avg_lead"] - b["avg_lead"], pctl,
                 is_anomaly=bool((c["avg_lead"] - b["avg_lead"]) > TH["LEAD_DELTA_DAYS"]),
                 threshold=TH["LEAD_DELTA_DAYS"], flags=fl_))
    pctdl, fdl = pct_change(b["avg_delay"], c["avg_delay"])
    M.append(rec("M18", "delivery_delays_mean", b["avg_delay"], c["avg_delay"],
                 c["avg_delay"] - b["avg_delay"], pctdl,
                 is_anomaly=bool(c["delayed"] > 0), threshold=0.0, flags=fdl)
             | {"delayed_po_count_baseline": b["delayed"], "delayed_po_count_current": c["delayed"],
                "delay_histogram": {str(k): sum(1 for r in po if r["_delay"] == k)
                                    for k in sorted({r["_delay"] for r in po})}})

    abnormal = [r["po_id"] for r in po
                if r["_delay"] >= TH["DELAY_ABNORMAL_DAYS"]
                or r["status"] != "Delivered"
                or to_date(r["delivery_date"]) > CURRENT[1]]
    abnormal_b = [r["po_id"] for r in po if r["_p"] == "BASELINE" and r["po_id"] in abnormal]
    M.append(rec("M19", "abnormally_delayed_pos", len(abnormal_b), len(abnormal),
                 len(abnormal) - len(abnormal_b), None,
                 is_anomaly=bool(len(abnormal) > 0), threshold=TH["DELAY_ABNORMAL_DAYS"],
                 flags=["base_zero"] if not abnormal_b else [])
             | {"abnormal_po_ids": abnormal})

    # ---- SUPPLIERS ----
    for s in sup_rows:
        sid = s["supplier_id"]
        g = {"period": None, "product_id": s["product_id"], "supplier_id": sid}
        pctlt, flt = pct_change(s["baseline_avg_lead_days"], s["current_avg_lead_days"])
        M.append(rec("M20", "supplier_lead_time_change", s["baseline_avg_lead_days"],
                     s["current_avg_lead_days"],
                     s["current_avg_lead_days"] - s["baseline_avg_lead_days"], pctlt,
                     is_anomaly=bool(s["current_avg_lead_days"] - s["baseline_avg_lead_days"] > 0),
                     threshold=0.0, flags=flt + ["no_period_split"], group=g)
                 | {"lead_time_vs_expected_days": s["current_avg_lead_days"] - s["expected_lead_time_days"]})
        pctuc, fuc = pct_change(s["baseline_unit_cost"], s["current_unit_cost"])
        fl_uc = list(fuc) + (["small_base"] if s["baseline_unit_cost"] < 1 else []) + ["cost_granularity:two_point_only"]
        M.append(rec("M21", "unit_cost_change", s["baseline_unit_cost"], s["current_unit_cost"],
                     s["current_unit_cost"] - s["baseline_unit_cost"], pctuc,
                     is_anomaly=bool(s["current_unit_cost"] - s["baseline_unit_cost"] > 0),
                     threshold=0.0, flags=fl_uc, group=g))
        M.append(rec("M22a", "otd_reported_pct", None, s["on_time_delivery_rate_pct"], None, None,
                     is_anomaly=bool(s["on_time_delivery_rate_pct"] < TH["OTD_MIN_PCT"]),
                     threshold=TH["OTD_MIN_PCT"], flags=["no_period_split"], group=g))
        agg = {}
        for period in ("BASELINE", "CURRENT"):
            sel = [r for r in po if r["supplier_id"] == sid and r["_p"] == period]
            on = sum(1 for r in sel if r["supplier_lead_days"] <= r["_exp"])
            agg[period] = (on / len(sel) * 100.0) if sel else None
        pcto, fo = pct_change(agg["BASELINE"], agg["CURRENT"])
        allsel = [r for r in po if r["supplier_id"] == sid]
        all_otd = (sum(1 for r in allsel if r["supplier_lead_days"] <= r["_exp"]) / len(allsel) * 100.0
                   if allsel else None)
        gap = (s["on_time_delivery_rate_pct"] - all_otd) if all_otd is not None else None
        M.append(rec("M22b", "otd_derived_pct", agg["BASELINE"], agg["CURRENT"], None, None,
                     pp=(agg["CURRENT"] - agg["BASELINE"]) if None not in (agg["BASELINE"], agg["CURRENT"]) else None,
                     is_anomaly=bool(agg["CURRENT"] is not None and agg["CURRENT"] < TH["OTD_MIN_PCT"]),
                     threshold=TH["OTD_MIN_PCT"], flags=fo, group=g)
                 | {"reported_vs_derived_gap_pp": None if gap is None else round(gap, 4)})

    # ---- CUSTOMER ----
    cagg = {}
    for period in ("BASELINE", "CURRENT"):
        sel = [r for r in fb if r["_p"] == period]
        n = len(sel)
        comp = [r for r in sel if r["complaint_type"] not in ("None", "", None)]
        types = {}
        for r in comp:
            types[r["complaint_type"]] = types.get(r["complaint_type"], 0) + 1
        cagg[period] = {
            "n": n, "complaints": len(comp),
            "rate": len(comp) / n * 100.0 if n else None,
            "refunds": sum(1 for r in sel if r["refund"] == "Yes"),
            "refund_rate": sum(1 for r in sel if r["refund"] == "Yes") / n * 100.0 if n else None,
            "cancels": sum(1 for r in sel if r["order_cancelled"] == "Yes"),
            "cancel_rate": sum(1 for r in sel if r["order_cancelled"] == "Yes") / n * 100.0 if n else None,
            "rating": sum(r["rating"] for r in sel) / n if n else None,
            "types": types,
            "share": {k: v / len(comp) * 100.0 for k, v in types.items()} if comp else {},
        }
    b, c = cagg["BASELINE"], cagg["CURRENT"]
    pctc_, fc_ = pct_change(b["complaints"], c["complaints"])
    M.append(rec("M23", "complaint_count", b["complaints"], c["complaints"],
                 c["complaints"] - b["complaints"], pctc_,
                 is_anomaly=bool((pctc_ is not None and pctc_ >= 20) or (c["complaints"] - b["complaints"]) >= 3),
                 threshold=20.0, flags=fc_ + ["denominator:feedback_records"])
             | {"feedback_records_baseline": b["n"], "feedback_records_current": c["n"]})
    for mid, name, key, thr, flag in [
        ("M24", "complaint_rate_pct", "rate", TH["COMPLAINT_RATE_PP"], "denominator:feedback_records"),
        ("M25", "refund_rate_pct", "refund_rate", 0.0, "denominator:feedback_records"),
        ("M26", "cancellation_rate_pct", "cancel_rate", 0.0, "denominator:feedback_records"),
    ]:
        bb, cc = b[key], c[key]
        pp = (cc - bb) if None not in (bb, cc) else None
        if mid == "M24":
            anom = bool(pp is not None and pp >= thr)
            fl = ["denominator:feedback_records"]
        else:
            anom = bool(c["refunds" if mid == "M25" else "cancels"] > 0
                        and b["refunds" if mid == "M25" else "cancels"] == 0)
            fl = ["denominator:feedback_records", "base_zero"]
        M.append(rec(mid, name, bb, cc, None, None, pp=pp, is_anomaly=anom,
                     threshold=thr, flags=fl))
    pctr, fr = pct_change(b["rating"], c["rating"])
    M.append(rec("M27", "avg_customer_rating", b["rating"], c["rating"],
                 c["rating"] - b["rating"], pctr,
                 is_anomaly=bool((c["rating"] - b["rating"]) <= TH["RATING_DELTA"]),
                 threshold=TH["RATING_DELTA"],
                 flags=fr + (["direction:down"] if c["rating"] < b["rating"] else []))
             | {"n_baseline": b["n"], "n_current": c["n"]})
    for t in sorted(set(b["types"]) | set(c["types"])):
        bc, cc = b["types"].get(t, 0), c["types"].get(t, 0)
        bs, cs_ = b["share"].get(t, 0.0), c["share"].get(t, 0.0)
        M.append(rec("M28", "complaint_type_change", bc, cc, cc - bc, None, pp=cs_ - bs,
                     is_anomaly=bool(abs(cs_ - bs) >= TH["COMPLAINT_TYPE_PP"] or (bc == 0 and cc > 0)),
                     threshold=TH["COMPLAINT_TYPE_PP"],
                     group={"period": None, "product_id": None, "supplier_id": None})
                 | {"complaint_type": t, "share_baseline_pct": round(bs, 4),
                    "share_current_pct": round(cs_, 4)})
    return M


# --------------------------------------------------------------------------

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Choo Timm Jiit\Downloads\RootIQ_SME_Dataset_Scenario1.xlsx"
    out = sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\Choo Timm Jiit\WorkBuddy AI\2026-10-10-13-37-10\rootiq_metric_reference_values.json"
    D = load(src)
    validate(D)
    M = compute(D)
    payload = {
        "spec_version": "1.0",
        "source_workbook": src,
        "periods": {"BASELINE": [str(BASELINE[0]), str(BASELINE[1])],
                    "CURRENT": [str(CURRENT[0]), str(CURRENT[1])],
                    "days_each": PERIOD_DAYS},
        "thresholds": TH,
        "metrics": M,
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    anomalies = [m["metric_id"] + "/" + str(m["group"].get("product_id") or m["group"].get("supplier_id") or "")
                 for m in M if m["is_anomaly"]]
    print(f"validated OK; {len(M)} metric records written to {out}")
    print(f"anomaly records: {len(anomalies)} -> {anomalies}")


if __name__ == "__main__":
    main()
