# SME Business Data Analyzer — Skill Prompt

This document preserves the exact WorkBuddy Skill instruction/prompt used to create and configure the SME Business Data Analyzer. The content below is extracted from the Skill's `SKILL.md` frontmatter and body, which serves as the instruction set the agent follows when this Skill is invoked.

---

## YAML Frontmatter

```yaml
---
name: sme-business-data-analyzer
description: >-
  Deterministic SME business data analyzer. Reads a multi-sheet Excel workbook
  or separate CSV files, validates schema, parses dates and numerics safely,
  reports data-quality issues, compares a BASELINE period against a CURRENT
  period, computes business metrics across sales, inventory, procurement,
  supplier, customer, and operations areas, detects anomalies using
  configurable rules, ranks them by composite score, and emits structured
  JSON + CSV. No root-cause reasoning. No LLM estimation. Every number comes
  from code.
agent_created: true
---
```

---

## Skill Instructions

### Purpose

This skill provides a **reusable, deterministic data-analysis engine** for SME operational data. It is designed to be the quantitative foundation layer for downstream AI investigators (e.g. RootIQ) that perform root-cause analysis.

**What this skill does:**
- Loads SME data from an Excel workbook (`.xlsx`/`.xls`) or separate CSV files
- Validates schema, data types, and data-quality identities
- Tags every row with a period (BASELINE / CURRENT / OUTSIDE)
- Computes metrics across 6 business areas
- Detects anomalies using user-specified threshold rules
- Ranks anomalies by composite score (magnitude x relevance)
- Outputs `analysis_summary.json` and `analysis_summary.csv`

**What this skill does NOT do:**
- Root-cause reasoning or business recommendations
- LLM estimation of calculable values
- Imputation, forward-fill, or outlier removal
- Modifying source files

---

### Process

When invoked, this skill executes the following pipeline:

1. **Load** — Detect input type (Excel workbook, single CSV, directory of CSVs, or list of CSV paths). Load all available sheets/dataframes.
2. **Validate & clean** — For each sheet: check required columns, parse date columns, coerce numeric columns, detect missing values and sentinel values (e.g. Excel text "None" in `complaint_type`), run data-quality identity checks, detect duplicate rows.
3. **Tag periods** — Assign every row to BASELINE, CURRENT, or OUTSIDE using the sheet's primary date column.
4. **Compute metrics** — Run all applicable metric computations for each detected dataset area.
5. **Detect anomalies** — Evaluate every computed metric against the configured anomaly rules.
6. **Rank anomalies** — Sort by composite score (magnitude_ratio x relevance_weight x 10) descending.
7. **Build result** — Assemble the structured JSON output with all sections.
8. **Save** — Write `analysis_summary.json` and `analysis_summary.csv` to the output directory.

---

### Strict Rules

1. **No fabrication.** Every numerical value in the output must originate from a deterministic calculation on the source data. Never invent, estimate, or round-fill a value.

2. **No root-cause reasoning.** This skill reports *what changed and by how much*, never *why*. No business recommendations.

3. **No silent inference.** Missing values are reported, not imputed. Sentinel values (e.g. Excel "None" text) are detected and flagged.

4. **No source modification.** The input workbook/CSVs are never written to or modified.

5. **Zero-base guard.** When baseline is 0, `PCT_CHANGE` returns `null` with `base_zero` flag. Never coerce to 0, 100, or infinity.

6. **Period integrity.** Period windows are inclusive constants. Rows outside both periods are tagged `OUTSIDE` and reported, never silently dropped.

7. **Deterministic output.** All sorts use explicit tie-break keys. The same input always produces the same output.

8. **Backward compatibility.** The output JSON maintains `analysis_summary.json` as the filename. Anomaly records include both new fields (`current_value`, `absolute_change`, `percentage_change`, `time_period`) and backward-compatible aliases (`current`, `change_pct`).

---

### Anomaly Detection Rules

| Rule key | Type | Threshold | Relevance | Label |
|---|---|---|---|---|
| `revenue` | pct_le | -10.0% | 10 | Revenue decline |
| `product_revenue` | pct_le | -15.0% | 9 | Product revenue decline |
| `stockout_hours` | stockout | 2x base or >8h | 8 | Stockout hours surge |
| `po_approval_time` | approval | >2d or >1.5x base | 7 | PO approval time spike |
| `supplier_lead_time` | mult_gt | 1.5x base | 7 | Supplier lead-time increase |
| `unit_cost` | pct_ge | +10.0% | 5 | Unit-cost increase |
| `complaint_rate` | pct_ge | +50.0% | 6 | Complaint-rate increase |
| `refund_rate` | pct_ge | +50.0% | 6 | Refund-rate increase |
| `fulfilment_time` | pct_ge | +30.0% | 7 | Fulfilment-time increase |
| `late_orders` | pct_ge | +50.0% | 7 | Late-order increase |
| `ops_capacity` | pct_le | -15.0% | 6 | Operational capacity drop |
| `ops_fulfilment` | pct_ge | +30.0% | 7 | Operations fulfilment-time increase |
| `ops_late_orders` | pct_ge | +50.0% | 7 | Operations late-order increase |
| `gross_profit` | pct_le | -10.0% | 9 | Gross-profit decline |
| `gross_margin` | pp_le | -3.0pp | 8 | Gross-margin decline |
| `cogs_increase` | pct_ge | +10.0% | 6 | COGS increase |
| `sales_unit_cost` | pct_ge | +10.0% | 6 | Sales unit-cost increase |
| `ops_staff_shortfall` | pct_le | -10.0% | 8 | Operations staff shortfall |
| `ops_fulfilment_rate` | pp_le | -5.0pp | 7 | Fulfilment-rate decline |

### Severity Bands

| Score range | Severity |
|---|---|
| >= 100 | CRITICAL |
| >= 50 | HIGH |
| >= 20 | MEDIUM |
| >= 1 | LOW |
| < 1 | INFO |

Score = `magnitude_ratio x relevance_weight x 10`

---

### Usage

#### CLI

```bash
python scripts/sme_analyzer.py <source> [--out-dir <dir>] \
    [--baseline-start 2026-08-03] [--baseline-end 2026-08-30] \
    [--current-start 2026-08-31] [--current-end 2026-09-27]
```

`<source>` can be:
- Path to an Excel workbook (`.xlsx` / `.xls`)
- Path to a single CSV file
- Path to a directory containing CSV files
- Comma-separated list of CSV file paths

#### Library

```python
from sme_analyzer import SMEBusinessDataAnalyzer
from datetime import date

analyzer = SMEBusinessDataAnalyzer(
    "path/to/workbook.xlsx",
    baseline_period=(date(2026, 8, 3), date(2026, 8, 30)),
    current_period=(date(2026, 8, 31), date(2026, 9, 27)),
    out_dir="path/to/output",
)
result = analyzer.run()
```

---

### Validation

After running the analyzer, compare its numerical output against known reference values. The validation checks:

1. **Business summary** — revenue baseline, current, and change % must match.
2. **Metric counts** — each section must contain the expected number of metrics.
3. **Key metric values** — spot-check critical metrics against reference values.
4. **Anomaly count** — the number of detected anomalies must match.
5. **Anomaly labels** — each detected anomaly must match its expected label and affected area.
6. **Severity** — anomaly severity must be in the correct band.

Any difference is reported as a validation difference. A difference in a core metric value (revenue, anomaly count) constitutes a FAIL. A difference in a non-core field (e.g. extra warning, rounding precision) constitutes a PASS WITH WARNINGS.

---

### Dependencies

- Python 3.10+
- pandas
- openpyxl (for Excel input)
