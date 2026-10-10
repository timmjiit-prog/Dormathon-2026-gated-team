# SME Business Data Analyzer

## Skill Name

`sme-business-data-analyzer`

## Purpose

A reusable, deterministic data-analysis engine for SME operational data. It loads a multi-sheet Excel workbook or separate CSV files, validates schema and data quality, compares a BASELINE period against a CURRENT period, computes business metrics across six operational areas, detects anomalies using configurable threshold rules, ranks them by composite score, and emits structured JSON + CSV.

Every number in the output originates from deterministic code on source data — no LLM estimation, no imputation, no fabrication.

## Role Inside RootIQ

This Skill is the **quantitative foundation layer** of the RootIQ Autonomous Root Cause Investigator pipeline. It sits at step 4 of the 14-step RootIQ architecture:

```
Receive → Understand → Plan → [ANALYZE] → Route → Map → Investigate
                                              ↑
                                   SME Business Data Analyzer
```

The analyzer produces `analysis_summary.json`, which downstream components consume:

| Downstream Component | How It Uses the Output |
|---|---|
| **RootIQ Mapper** (`rootiq_mapper.py`) | Converts the multi-section JSON into a flat metrics payload for the Teammate2 engine |
| **RootIQ Orchestrator** (`rootiq_orchestrator.py`) | Reads ranked anomalies, business summary, and per-area evidence to drive hypothesis generation and self-disproof |
| **Sales Performance Investigator** (Expert agent) | Consumes `product_findings`, `overall_metrics`, and `ranked_anomalies` to generate ranked hypotheses |
| **Customer & Operations Investigator** (Expert agent) | Consumes `customer_evidence`, `operations_evidence` to investigate complaints and delivery issues |
| **Evidence Validator** (Teammate2 role 2D) | Cross-checks ranked anomalies against the structured evidence to validate or reject hypotheses |
| **Corrective Action Executor** (Skill) | Uses quantified impact and anomaly details to generate SMART corrective actions |
| **Handoff JSON** (`scenario_N_handoff.json`) | The analyzer's output is transformed into a standardized handoff package that wraps all evidence for downstream consumption |

The analyzer never performs root-cause reasoning, never ranks remedies, and never asserts causal links. It reports *what changed and by how much* — downstream agents handle *why*.

## Supported Inputs

### Multi-Sheet Excel Workbook

A single `.xlsx` or `.xls` file containing some or all of these sheets:

| Sheet | Required Columns |
|---|---|
| `Sales` | `date`, `order_id`, `product_id`, `quantity`, `unit_price`, `revenue` (optional: `unit_cost`, `cogs`, `gross_profit`) |
| `Inventory` | `date`, `product_id`, `opening_stock`, `received`, `sold`, `closing_stock`, `stockout_hours` |
| `Purchase_Orders` | `po_id`, `product_id`, `supplier_id`, `request_date`, `approval_date`, `order_date`, `delivery_date`, `quantity`, `status`, `approval_days`, `supplier_lead_days` |
| `Suppliers` | `supplier_id`, `product_id`, `expected_lead_time_days`, `baseline_avg_lead_days`, `current_avg_lead_days`, `baseline_unit_cost`, `current_unit_cost`, `on_time_delivery_rate_pct` |
| `Customer_Feedback` | `date`, `feedback_id`, `product_id`, `complaint_type`, `rating`, `refund`, `order_cancelled` |
| `Operations` | `date`, `shift` (optional), `required_staff`, `scheduled_staff`, `actual_staff`, `orders_received`, `capacity_orders`, `orders_fulfilled`, `late_orders`, `avg_fulfilment_hours` (legacy: `staff_count`, `operational_capacity_pct`, `fulfilment_time_hours`) |

### Separate CSV Files

One CSV per dataset, matched case-insensitively by filename (underscores, spaces, and hyphens are treated as equivalent). Example: `sales.csv`, `inventory.csv`, `purchase_orders.csv`, `suppliers.csv`, `customer_feedback.csv`, `operations.csv`.

### Missing Sheets

If a sheet is absent, its metric section is emitted as an empty array `[]`. The analyzer never fails because an optional sheet is missing.

## Supported Datasets

The analyzer handles six business areas, each independently:

| Area | Source Sheet | Key Metrics |
|---|---|---|
| **Sales** | `Sales` | Revenue, units sold, selling price, revenue contribution, COGS, gross profit, gross margin, unit cost |
| **Inventory** | `Inventory` | Stockout hours, stockout days, closing stock, availability % |
| **Procurement** | `Purchase_Orders` | Approval time, supplier lead time, fulfilment time, late orders |
| **Suppliers** | `Suppliers` | Lead time change, unit cost change, on-time delivery (reported + derived) |
| **Customer** | `Customer_Feedback` | Complaint count, complaint rate, refund rate, cancellation rate, average rating, complaint type mix |
| **Operations** | `Operations` | Actual/required staff, staffing gap, orders received/fulfilled, fulfilment rate, capacity orders, capacity utilization, late orders, fulfilment time — overall and per-shift |

## Main Calculations

### Period Comparison

Every metric is computed for both periods and compared:

- **PCT_CHANGE(base, current)** = `(current - base) / base * 100` — relative change (%)
- **PP_CHANGE(base, current)** = `current - base` — absolute percentage-point change (for rates)
- **DELTA(base, current)** = `current - base` — absolute change in native units

### Zero-Base Guard

When baseline is 0, `PCT_CHANGE` returns `null` with `base_zero = true`. Never coerced to 0, 100, or infinity.

### Profit Metrics (Optional)

When `Sales` contains `unit_cost`, `cogs`, and `gross_profit` columns:

- Overall and per-product: COGS, gross profit, gross margin %, average unit cost
- Anomaly rules: gross profit decline (<= -10%), gross margin decline (<= -3pp), COGS increase (>= +10%), sales unit cost increase (>= +10%)

### Operations Metrics (When Sheet Present)

Overall and per-shift breakdown of staffing, capacity, late orders, and fulfilment time.

### Anomaly Detection

19 configurable rules across all areas. Each rule has a threshold, relevance weight, and human-readable label. Composite score = `magnitude_ratio * relevance_weight * 10`. Severity bands: CRITICAL (>= 100), HIGH (>= 50), MEDIUM (>= 20), LOW (>= 1), INFO (< 1).

### Data Quality Identities

- `revenue == quantity * unit_price`
- `cogs == quantity * unit_cost`
- `gross_profit == revenue - cogs`
- `closing_stock == opening_stock + received - sold`
- `approval_days == approval_date - request_date`

## Output Format

Two files are produced in the output directory:

### analysis_summary.json

Structured JSON with these top-level keys:

```
business_summary       — periods + overall revenue (and profit metrics if available)
product_metrics        — per-product revenue, units, price, contribution, profit
inventory_metrics      — per-product stockout, closing stock, availability
procurement_metrics    — overall + per-product approval, lead time, fulfilment, late orders
supplier_metrics       — per-supplier lead time, unit cost, OTD (reported + derived)
customer_metrics       — complaint count/rate, refund rate, cancellation rate, rating, complaint types
operations_metrics     — overall + per-shift staffing, capacity, late orders, fulfilment time
anomalies              — ranked list with baseline, current, change, severity, evidence_source
data_quality           — missing values, invalid values, warnings
```

Each metric entry: `identifier`, `metric`, `baseline`, `current`, `change_pct`, `severity`, plus optional `base_zero`, `pp_change`, `contribution_pct`.

Each anomaly entry: `metric` (label), `affected_area`, `baseline`, `current_value`, `absolute_change`, `percentage_change`, `severity`, `time_period`, `evidence_source`, plus backward-compatible aliases `current` and `change_pct`.

### analysis_summary.csv

Flat table: `category`, `identifier`, `metric`, `baseline`, `current`, `change_pct`, `severity`. One row per metric + one row per anomaly.

## Example Usage

### CLI

```bash
python scripts/sme_analyzer.py workbook.xlsx \
    --out-dir output/ \
    --baseline-start 2026-08-03 --baseline-end 2026-08-30 \
    --current-start 2026-08-31 --current-end 2026-09-27
```

### Python Library

```python
from sme_analyzer import SMEBusinessDataAnalyzer
from datetime import date

analyzer = SMEBusinessDataAnalyzer(
    "path/to/workbook.xlsx",
    baseline_period=(date(2026, 8, 3), date(2026, 8, 30)),
    current_period=(date(2026, 8, 31), date(2026, 9, 27)),
    out_dir="output/",
)
result = analyzer.run()

# result["business_summary"]    — headline metrics
# result["product_metrics"]     — per-product detail
# result["anomalies"]            — ranked anomalies
# result["data_quality"]        — validation report
```

### CSV Input

```python
analyzer = SMEBusinessDataAnalyzer(
    ["sales.csv", "inventory.csv", "purchase_orders.csv",
     "suppliers.csv", "customer_feedback.csv"]
)
result = analyzer.run()
```

## What the Skill Does NOT Do

1. **No root-cause reasoning.** Reports what changed and by how much, never why.
2. **No LLM estimation.** Every numerical value comes from deterministic code.
3. **No imputation.** Missing values are reported, not filled.
4. **No outlier removal.** Outliers are reported, not cleaned.
5. **No source modification.** Input files are never written to or modified.
6. **No business recommendations.** No remedies ranked, no management advice.
7. **No causal inference.** Correlation between metrics is a downstream concern.

## Dependencies

- Python 3.10+
- pandas
- openpyxl (for Excel input)

## Files

```
sme-business-data-analyzer/
  SKILL.md                          — Skill configuration and documentation
  scripts/
    sme_analyzer.py                 — Main analyzer implementation (~1,599 lines)
  references/
    calculation_spec.md             — 28-metric calculation specification (M01-M28)
```

## How Downstream RootIQ Agents Use the Output

The analyzer's `analysis_summary.json` flows through the RootIQ pipeline in this sequence:

1. **Handoff JSON Creation**: The analyzer's structured output is mapped into a standardized `scenario_N_handoff.json` with top-level keys for each evidence area (`overall_metrics`, `product_findings`, `inventory_evidence`, `procurement_evidence`, `supplier_evidence`, `customer_evidence`, `operations_evidence`, `ranked_anomalies`, `data_quality`). Values are copied verbatim — no new computation, no fabrication.

2. **RootIQ Mapper** (`rootiq_mapper.py`): The handoff JSON is converted into the flat metrics payload expected by the Teammate2 deterministic engine. Key mappings:
   - `overall_metrics.revenue_change_pct` → `metrics.overall_revenue_change_pct`
   - `inventory_evidence[].total_stockout_hours` → `metrics.stockout_hours`
   - `procurement_evidence[].avg_approval_time_days` → `metrics.po_approval_days`
   - `procurement_evidence[].avg_supplier_lead_time_days` → `metrics.supplier_lead_days`
   - `customer_evidence.complaint_count` delta → `metrics.complaints_change_pct`
   - Revenue loss → `impacts[hypothesis].lost_revenue`

3. **Teammate2 Engine** (`rootiq.py`): The mapped payload drives hypothesis ranking (roles 2A Inventory/Procurement, 2B Customer/Operations), hypothesis comparison (2C), and evidence validation (2D with 8 checks).

4. **RootIQ Orchestrator** (`rootiq_orchestrator.py`): Uses the ranked anomalies to drive self-disproof (5 dimensions), impact quantification, and corrective action generation (SMART criteria).

5. **Specialist Investigators**: Sales Investigator consumes product/sales evidence; Customer & Operations Investigator consumes customer/operations evidence.

The strict separation ensures that the factual layer (this Skill) and the reasoning layer (downstream agents) never mix — every conclusion in the final report can be traced back to a specific computed value in `analysis_summary.json`.
