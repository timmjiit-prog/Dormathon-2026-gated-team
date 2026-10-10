# RootIQ — Deterministic Calculation Specification (v1.0)

**Purpose.** This document specifies every calculation the RootIQ data-analysis layer must run **before** an AI investigator sees any result. All metrics are deterministic, reproducible and implementable in plain Python/SQL. No LLM inference, no estimation, no imputation is used anywhere in this layer.

**Source workbook:** `RootIQ_SME_Dataset_Scenario1.xlsx`  
**Sheets:** `Guide` (metadata — excluded), `Sales`, `Inventory`, `Purchase_Orders`, `Suppliers`, `Customer_Feedback`  
**Scope:** calculation design + reference values. **No root-cause reasoning, no business recommendations.**

---

## 0. Shared conventions

These definitions apply to every metric below. Implement them once, in one module, and reuse.

### 0.1 Period windows

| Period     | Start      | End        | Days |
| ---------- | ---------- | ---------- | ---- |
| `BASELINE` | 2026-08-03 | 2026-08-30 | 28   |
| `CURRENT`  | 2026-08-31 | 2026-09-27 | 28   |

Both windows are **inclusive on both ends**. The windows are adjacent (no gap) and equally long, so no day-count normalisation is required for level metrics.

### 0.2 Period-assignment rule (which date column decides the period)

| Sheet                                     | Period-assigning column | Rationale                                                                                   |
| ----------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------- |
| `Sales`                                   | `date`                  | transaction date                                                                            |
| `Inventory`                               | `date`                  | daily snapshot date                                                                         |
| `Customer_Feedback`                       | `date`                  | feedback date                                                                               |
| `Purchase_Orders`                         | `request_date`          | **primary** rule — the PO belongs to the period in which it was raised                      |
| `Purchase_Orders` (delivery metrics only) | `delivery_date`         | used only where the metric is about the delivery event                                      |
| `Suppliers`                               | none                    | table has no date column; its `baseline_*` / `current_*` columns are already pre-aggregated |

### 0.3 Row classification

Every row gets `period ∈ {BASELINE, CURRENT, OUTSIDE}`. `OUTSIDE` rows are never silently dropped — they are counted and reported. Known `OUTSIDE` row: `Purchase_Orders.PO006` (`approval_date`/`order_date` = 2026-09-28, `delivery_date` = 2026-10-03).

### 0.4 Change formulas

```
PCT_CHANGE(B, C) = (C - B) / B * 100        # relative change, %
PP_CHANGE(B, C)  =  C - B                   # absolute change, percentage points (rates only)
DELTA(B, C)      =  C - B                   # absolute change, native units
```

**Zero-base rule (mandatory):** if `B == 0`, `PCT_CHANGE` returns `null` and sets flag `base_zero = true`. It must **never** be coerced to `0`, `100` or `inf`. Consumers must branch on `base_zero`.

### 0.5 Numeric hygiene

- Keep full float precision internally; round only at serialisation (`2 dp` for currency and %, `1 dp` for days, `2 dp` for ratings).
- Division by zero → `null` + flag, never `0`.
- No imputation. No forward-fill. No outlier removal (outliers are *reported*, not *cleaned*).
- Empty group (no rows in a period) → `null` for every aggregate of that group, plus flag `no_rows`.

### 0.6 Anomaly thresholds — default configuration

All thresholds are named constants so the investigator layer can tune them without touching formulas.

| Constant                 | Default | Meaning                                        |
| ------------------------ | ------- | ---------------------------------------------- |
| `TH_REVENUE_PCT`         | 10.0    | material revenue movement (%)                  |
| `TH_CONTRIB_DOMINANT`    | 50.0    | dominant contributor share of total change (%) |
| `TH_STOCKOUT_DAYS`       | 1       | any stockout day is an anomaly                 |
| `TH_AVAILABILITY_PP`     | -2.0    | availability drop (pp)                         |
| `TH_CLOSING_STOCK_PCT`   | -25.0   | closing-stock decline (%)                      |
| `TH_APPROVAL_DELTA_DAYS` | 1.0     | approval-time increase (days)                  |
| `TH_APPROVAL_PCT`        | 100.0   | approval-time increase (%)                     |
| `TH_LEAD_DELTA_DAYS`     | 0.0     | any lead-time increase                         |
| `TH_DELAY_ABNORMAL_DAYS` | 2       | PO delay counted as abnormal (days)            |
| `TH_OTD_MIN_PCT`         | 90.0    | on-time-delivery floor (%)                     |
| `TH_COMPLAINT_RATE_PP`   | 5.0     | complaint-rate increase (pp)                   |
| `TH_RATING_DELTA`        | -0.25   | rating drop                                    |
| `TH_COMPLAINT_TYPE_PP`   | 20.0    | complaint-mix shift (pp)                       |

### 0.7 Determinism rules

- Sorting is always explicit and total: primary key ascending, then `product_id` / `po_id` / `supplier_id` ascending. Never rely on file order or dict order.
- Every metric returns a record `{metric_id, value_baseline, value_current, delta, pct_change, pp_change, is_anomaly, flags, threshold_used}`.
- Reference values in §6 were produced by the companion implementation `rootiq_metrics.py`, not by hand.

---

## 1. SALES ANALYSIS

### M01 · Total revenue by period

- **Formula:** `SUM(revenue)`
- **Required columns:** `Sales.date`, `Sales.revenue`
- **Grouping level:** period (whole dataset)
- **Baseline:** `SUM(revenue) WHERE period = BASELINE` → **39,975.00** (163 orders)
- **Current:** `SUM(revenue) WHERE period = CURRENT` → **32,660.00** (159 orders)
- **% change:** `PCT_CHANGE` → **−18.30%** (Δ = −7,315.00)
- **Anomaly:** `abs(pct_change) >= TH_REVENUE_PCT (10%)` → **−18.30% → ANOMALY**

### M02 · Revenue percentage change

- **Formula:** `(rev_current - rev_baseline) / rev_baseline * 100`
- **Required columns:** `Sales.date`, `Sales.revenue`
- **Grouping level:** period
- **Baseline:** `rev_baseline = 39,975.00` (reference value)
- **Current:** `rev_current = 32,660.00` (reference value)
- **% change:** **−18.30%**; absolute change **−7,315.00**; `base_zero = false`
- **Anomaly:** `abs(pct_change) >= 10%` **or** `base_zero = true` (an undefined change is itself reportable) → **ANOMALY**

> M02 is the same arithmetic as M01 but is specified separately because it is the headline scalar the investigator receives; it must be emitted as a first-class field, not recomputed downstream.

### M03 · Revenue by product

- **Formula:** `SUM(revenue)` grouped by `product_id`
- **Required columns:** `Sales.date`, `Sales.product_id`, `Sales.revenue`
- **Grouping level:** `product_id` × period
- **Baseline:** P001 = **30,310.00** · P002 = **5,940.00** · P003 = **3,725.00**
- **Current:** P001 = **22,680.00** · P002 = **6,180.00** · P003 = **3,800.00**
- **% change:** per product — see M04
- **Anomaly:** any product whose revenue falls by ≥ 10% of *its own* baseline → P001 only

### M04 · Revenue percentage change by product

- **Formula:** `(rev_cur_p - rev_base_p) / rev_base_p * 100` for each `p`
- **Required columns:** `Sales.date`, `Sales.product_id`, `Sales.revenue`
- **Grouping level:** `product_id`
- **Baseline:** P001 30,310 · P002 5,940 · P003 3,725
- **Current:** P001 22,680 · P002 6,180 · P003 3,800
- **% change:** P001 = **−25.17%** (Δ −7,630) · P002 = **+4.04%** (Δ +240) · P003 = **+2.01%** (Δ +75)
- **Anomaly:** `abs(pct_change) >= 10%` → **P001 → ANOMALY**; P002/P003 normal

### M05 · Units sold by product

- **Formula:** `SUM(quantity)` grouped by `product_id`
- **Required columns:** `Sales.date`, `Sales.product_id`, `Sales.quantity`
- **Grouping level:** `product_id` × period (dataset total: 780 → 682)
- **Baseline:** P001 = **433** · P002 = **198** · P003 = **149**
- **Current:** P001 = **324** · P002 = **206** · P003 = **152**
- **% change:** per product — see M06
- **Anomaly:** any product whose units fall ≥ 10% of its own baseline → P001 only

### M06 · Units-sold percentage change

- **Formula:** `(qty_cur_p - qty_base_p) / qty_base_p * 100`
- **Required columns:** `Sales.date`, `Sales.product_id`, `Sales.quantity`
- **Grouping level:** `product_id` (and dataset total)
- **Baseline:** total 780 · P001 433 · P002 198 · P003 149
- **Current:** total 682 · P001 324 · P002 206 · P003 152
- **% change:** total **−12.56%** · P001 **−25.17%** · P002 **+4.04%** · P003 **+2.01%**
- **Anomaly:** `abs(pct_change) >= 10%` → total and P001 → **ANOMALY**

### M07 · Selling-price change

Two distinct quantities must be computed and kept separate — conflating them is a known analytical error.

**(a) Unit list price per product**

- **Formula:** `realised_price(p) = SUM(revenue) / SUM(quantity)` per product per period; also `DISTINCT(unit_price)` per product as a validation
- **Required columns:** `Sales.date`, `Sales.product_id`, `Sales.quantity`, `Sales.unit_price`, `Sales.revenue`
- **Grouping level:** `product_id`
- **Baseline:** P001 = 70.00 · P002 = 30.00 · P003 = 25.00
- **Current:** P001 = 70.00 · P002 = 30.00 · P003 = 25.00
- **% change:** **0.00% for all three products** (`DISTINCT(unit_price)` returns exactly one value per product across the entire dataset, so the change is structurally zero)
- **Anomaly:** `abs(delta) > 0` for any product (any realised price movement is reportable) → **no anomaly**

**(b) Blended average selling price (mix-affected)**

- **Formula:** `SUM(revenue) / SUM(quantity)` across all products
- **Required columns:** `Sales.date`, `Sales.revenue`, `Sales.quantity`
- **Grouping level:** period
- **Baseline:** **51.25**
- **Current:** **47.89**
- **% change:** **−6.56%** (Δ −3.36)
- **Anomaly:** `abs(pct_change) >= 10%` → **no anomaly**; but must carry flag `mix_affected = true` because no product price changed, so the movement is a composition effect, not a price effect.

### M08 · Contribution of each product to the total revenue decline

- **Formula:** `contribution_p = (rev_cur_p - rev_base_p) / (rev_cur_total - rev_base_total) * 100`
- **Required columns:** `Sales.date`, `Sales.product_id`, `Sales.revenue`
- **Grouping level:** `product_id`
- **Baseline:** denominator `total_delta = −7,315.00`
- **Current:** contributions computed against the signed total delta
- **% change:** P001 = **+104.31%** · P002 = **−3.28%** · P003 = **−1.03%** (contributions sum to 100%)
- **Anomaly:** `abs(contribution) >= TH_CONTRIB_DOMINANT (50%)` **and** `sign(delta_p) == sign(total_delta)` → **P001 → DOMINANT CONTRIBUTOR**. Guard: if `total_delta == 0`, return `null` for every contribution + flag `zero_total_change`.

### M09 · Product ranking by negative revenue impact

- **Formula:** sort products by `revenue_delta` ascending (most negative first); `rank = 1..n`
- **Required columns:** `Sales.date`, `Sales.product_id`, `Sales.revenue`
- **Grouping level:** `product_id`
- **Baseline:** per-product revenue as in M03
- **Current:** per-product revenue as in M03
- **% change:** n/a (ordinal output); each row carries its own `revenue_delta`
- **Reference ranking:** **1. P001 (−7,630) · 2. P003 (+75) · 3. P002 (+240)**
- **Anomaly:** rank-1 product is an anomaly if `revenue_delta_1 < 0` and `abs(revenue_delta_1) >= 25%` of `abs(total_delta)` → **P001 (104.3%) → ANOMALY**. Tie-break: `product_id` ascending.



---

## 2. INVENTORY ANALYSIS

Inventory grain is one row per `date` × `product_id`; each product has exactly 28 rows per period. Stockout hours per day take only the values `0 / 3.4 / 11.2 / 12`.

### M10 · Total stockout hours by product
- **Formula:** `SUM(stockout_hours)` grouped by `product_id`
- **Required columns:** `Inventory.date`, `Inventory.product_id`, `Inventory.stockout_hours`
- **Grouping level:** `product_id` × period (dataset total: 0 → 86.6)
- **Baseline:** P001 = **0.0** · P002 = **0.0** · P003 = **0.0**
- **Current:** P001 = **86.6** · P002 = **0.0** · P003 = **0.0**
- **% change:** `null` + `base_zero = true` for P001 (baseline is 0 — must not be coerced). Report `DELTA = +86.6` instead.
- **Anomaly:** `current > 0` while `baseline == 0` (new occurrence) **or** `pct_change >= 50%` when baseline > 0 → **P001 → ANOMALY**

### M11 · Average stockout hours by product
- **Formula:** `SUM(stockout_hours) / COUNT(days in period)` — denominator is calendar days in the window (28), **not** days with data, so a missing day cannot inflate the mean
- **Required columns:** `Inventory.date`, `Inventory.product_id`, `Inventory.stockout_hours`
- **Grouping level:** `product_id` × period (dataset total: 0.00 → 1.03)
- **Baseline:** P001 = **0.000** · P002 = **0.000** · P003 = **0.000**
- **Current:** P001 = **3.093** · P002 = **0.000** · P003 = **0.000**
- **% change:** `null` + `base_zero = true` for P001; `DELTA = +3.093`
- **Anomaly:** `current > 0` with `baseline == 0` → **P001 → ANOMALY**

### M12 · Number of stockout days
- **Formula:** `COUNT(*) WHERE stockout_hours > 0` grouped by `product_id`
- **Required columns:** `Inventory.date`, `Inventory.product_id`, `Inventory.stockout_hours`
- **Grouping level:** `product_id` × period (dataset total: 0 → 8)
- **Baseline:** P001 = 0 · P002 = 0 · P003 = 0
- **Current:** P001 = **8** · P002 = 0 · P003 = 0
- **% change:** `null` + `base_zero = true` for P001; `DELTA = +8` days
- **Anomaly:** `stockout_days >= TH_STOCKOUT_DAYS (1)` → **P001 (8 days) → ANOMALY**
- **Companion field (report alongside):** `zero_stock_days = COUNT(*) WHERE closing_stock == 0` → P001 baseline 0 → current **8** (matches the stockout days exactly, which is a useful cross-check).

### M13 · Closing-stock trend
- **Formula (four components):**
  1. `avg_closing_stock = SUM(closing_stock) / 28`
  2. `slope_per_day = OLS slope of closing_stock ~ day_index` (day_index = days since 2026-08-03)
  3. `min_closing_stock`, `max_closing_stock`
  4. `pct_change_avg = PCT_CHANGE(avg_base, avg_cur)`
- **Required columns:** `Inventory.date`, `Inventory.product_id`, `Inventory.closing_stock`
- **Grouping level:** `product_id` × period
- **Baseline:** P001 avg **119.11**, slope **−1.331/day**, min 39, max 207 · P002 avg **140.39**, slope **+3.534/day** · P003 avg **113.93**, slope **+2.372/day**
- **Current:** P001 avg **47.07**, slope **+0.714/day**, min **0**, max 121 · P002 avg **214.32**, slope **+2.612/day** · P003 avg **196.86**, slope **+2.531/day**
- **% change:** P001 **−60.48%** · P002 **+52.66%** · P003 **+72.79%**
- **Anomaly:** `pct_change_avg <= TH_CLOSING_STOCK_PCT (−25%)` **or** `min_closing_stock == 0` **or** slope sign flips from positive to negative → **P001 → ANOMALY** (both conditions triggered); P002/P003 normal.

### M14 · Change in product availability
- **Formula:** `availability_pct = (1 - SUM(stockout_hours) / (24 * days_in_period)) * 100`
  Secondary variant: `availability_days_pct = (1 - stockout_days / days_in_period) * 100`
- **Required columns:** `Inventory.date`, `Inventory.product_id`, `Inventory.stockout_hours`
- **Grouping level:** `product_id` × period
- **Baseline:** P001 = **100.00%** · P002 = **100.00%** · P003 = **100.00%**
- **Current:** P001 = **87.11%** · P002 = **100.00%** · P003 = **100.00%**
- **% change:** use `PP_CHANGE` (percentage points), not `PCT_CHANGE` — P001 = **−12.89 pp** · P002 = 0.00 pp · P003 = 0.00 pp
- **Anomaly:** `pp_change <= TH_AVAILABILITY_PP (−2.0 pp)` → **P001 → ANOMALY**
- **Note:** the day-based variant gives P001 = 71.43% (a −28.57 pp drop). Both are correct; the hours-based figure is the primary because it is time-weighted. Emit both and label which is which.

---

## 3. PROCUREMENT ANALYSIS

`Purchase_Orders` has 17 rows: 9 assigned to `BASELINE` and 8 to `CURRENT` by `request_date`. `supplier_lead_days` equals `delivery_date − order_date` in every row (verified: 0 mismatches), so either can be used; prefer the stored column and assert the identity as a data-quality guard.

### M15 · Average PO approval time
- **Formula:** `AVG(approval_days)` (equivalently `AVG(approval_date - request_date)`)
- **Required columns:** `Purchase_Orders.request_date`, `Purchase_Orders.approval_date`, `Purchase_Orders.approval_days`
- **Grouping level:** period
- **Baseline:** **0.444 days** (9 POs, max 1)
- **Current:** **3.250 days** (8 POs, max **8**)
- **% change:** **+631.25%**; Δ = **+2.806 days**
- **Anomaly:** `delta >= TH_APPROVAL_DELTA_DAYS (1.0 day)` **or** `pct_change >= TH_APPROVAL_PCT (100%)` → **ANOMALY on both tests**. Also report `max_approval_days` as a distribution-tail guard.

### M16 · PO approval time by product
- **Formula:** `AVG(approval_days)` grouped by `product_id`
- **Required columns:** `Purchase_Orders.request_date`, `Purchase_Orders.product_id`, `Purchase_Orders.approval_days`
- **Grouping level:** `product_id` × period
- **Baseline:** P001 = **0.667** · P002 = **0.333** · P003 = **0.333**
- **Current:** P001 = **7.667** · P002 = **0.667** · P003 = **0.500**
- **% change:** P001 = **+1050.00%** (Δ +7.000) · P002 = **+100.00%** (Δ +0.333) · P003 = **+50.00%** (Δ +0.167)
- **Anomaly:** `delta >= 1.0 day` → **P001 → ANOMALY**. P002/P003 are below the absolute threshold and are flagged `small_base` because their baselines (< 0.5 day) make the percentage change misleadingly large — the absolute delta must be reported alongside.

### M17 · Average supplier lead time
- **Formula:** `AVG(supplier_lead_days)` (equivalently `AVG(delivery_date - order_date)`)
- **Required columns:** `Purchase_Orders.request_date`, `Purchase_Orders.delivery_date`, `Purchase_Orders.order_date`, `Purchase_Orders.supplier_lead_days`, `Purchase_Orders.product_id`, `Purchase_Orders.supplier_id`
- **Grouping level:** period; also `supplier_id` × period and `product_id` × period
- **Baseline:** overall **3.333 days** — P001 **3.0** · P002 **3.0** · P003 **4.0**
- **Current:** overall **4.000 days** — P001 **5.0** · P002 **3.0** · P003 **4.0**
- **% change:** overall **+20.00%** (Δ +0.667) · P001 **+66.67%** (Δ +2.0) · P002 **0.00%** · P003 **0.00%**
- **Anomaly:** `delta > TH_LEAD_DELTA_DAYS (0)` at `supplier_id` level → **S001 → ANOMALY**; overall is an anomaly because it is driven entirely by S001.

### M18 · Delivery delays
- **Formula:** `delay_days = supplier_lead_days - expected_lead_time_days`, where `expected_lead_time_days` comes from `Suppliers` joined on `product_id`
  Equivalent cross-check: `delay_days = (delivery_date - order_date) - expected_lead_time_days`
- **Required columns:** `Purchase_Orders.po_id`, `Purchase_Orders.product_id`, `Purchase_Orders.order_date`, `Purchase_Orders.delivery_date`, `Purchase_Orders.supplier_lead_days`, `Suppliers.product_id`, `Suppliers.expected_lead_time_days`
- **Grouping level:** `po_id` (row level); aggregated to `supplier_id` × period and period
- **Baseline:** mean delay **0.000 days**; 0 of 9 POs delayed
- **Current:** mean delay **0.750 days**; **3 of 8** POs delayed, each by exactly **+2 days** (`PO004`, `PO005`, `PO006`)
- **% change:** `null` + `base_zero = true` (baseline mean is 0). Report `DELTA = +0.750 days` and the delayed-PO count change `0 → 3`.
- **Anomaly:** `delay_days > 0` for any PO → **PO004, PO005, PO006 → ANOMALY**. Distribution guard: report the full histogram (`{0 days: 14 POs, +2 days: 3 POs}`) so a hidden tail cannot be averaged away.

### M19 · Abnormally delayed purchase orders
- **Formula (union of four deterministic tests, any one flags the PO):**
  1. `delay_days >= TH_DELAY_ABNORMAL_DAYS (2)`
  2. `status != 'Delivered'` (i.e. `Pending Delivery`)
  3. `delivery_date > period_end` (2026-09-27)
  4. Statistical: `delay_days > mean(baseline_delay) + 2 * stdev(baseline_delay)` — **guard:** baseline delays are all 0, so `stdev = 0` and this test degenerates; when `stdev == 0` the test must fall back to test 1, not evaluate to `delay > 0`.
- **Required columns:** `Purchase_Orders.po_id`, `Purchase_Orders.delay_days` (from M18), `Purchase_Orders.status`, `Purchase_Orders.delivery_date`
- **Grouping level:** `po_id`, rolled up to `supplier_id`
- **Baseline:** **0 abnormal POs**
- **Current:** **3 abnormal POs** — `PO004`, `PO005`, `PO006` (all four tests agree on this set)
- **% change:** `null` + `base_zero = true`; report `DELTA = +3 POs`
- **Anomaly:** `abnormal_po_count > 0` → **ANOMALY**; and if `> 50%` of a supplier's POs are abnormal, flag that supplier. S001 = 3 of 3 current POs abnormal → **supplier-level ANOMALY**.

---

## 4. SUPPLIER ANALYSIS

`Suppliers` is pre-aggregated: it carries `baseline_*` and `current_*` column pairs and **no date column**, so its own change metrics cannot be period-filtered — they are taken at face value. Where possible, each is cross-validated against a period-splittable PO-derived equivalent.

### M20 · Supplier lead-time change
- **Formula:** `lead_time_delta = current_avg_lead_days - baseline_avg_lead_days`; `lead_time_vs_expected = current_avg_lead_days - expected_lead_time_days`
- **Required columns:** `Suppliers.supplier_id`, `Suppliers.baseline_avg_lead_days`, `Suppliers.current_avg_lead_days`, `Suppliers.expected_lead_time_days`
- **Grouping level:** `supplier_id` (= `product_id`, the table is 1:1)
- **Baseline:** S001 = 3 · S002 = 3 · S003 = 4
- **Current:** S001 = **5** · S002 = 3 · S003 = 4
- **% change:** S001 = **+66.67%** (Δ **+2 days**) · S002 = **0.00%** · S003 = **0.00%**
- **Anomaly:** `delta > 0` → **S001 → ANOMALY**. Cross-validation: PO-derived lead time for S001 goes 3.0 → 5.0 (identical), so the pre-aggregated column is corroborated. `lead_time_vs_expected` for S001 = **+2 days** over contract.

### M21 · Unit-cost change
- **Formula:** `unit_cost_delta = current_unit_cost - baseline_unit_cost`; `PCT_CHANGE` of the same
- **Required columns:** `Suppliers.supplier_id`, `Suppliers.baseline_unit_cost`, `Suppliers.current_unit_cost`
- **Grouping level:** `supplier_id`
- **Baseline:** S001 = 34.00 · S002 = 14.00 · S003 = 11.00
- **Current:** S001 = **34.50** · S002 = 14.00 · S003 = **11.20**
- **% change:** S001 = **+1.47%** (Δ +0.50) · S002 = **0.00%** · S003 = **+1.82%** (Δ +0.20)
- **Anomaly:** `delta > 0` → **S001 and S003 → ANOMALY** (small in absolute terms; report the absolute delta and suppress the percentage when `baseline < 1.0` to avoid misleading magnitude).
- **Schema limitation:** cost exists only as a two-point baseline/current pair in `Suppliers`. There is **no per-PO or per-period cost column**, so cost change cannot be attributed to a specific PO or date, and cannot be volume-weighted. This must be carried as flag `cost_granularity = 'two_point_only'`.


### M22 · On-time delivery performance
Two independent measures — emit both, never merge them.

**(a) Reported rate**
- **Formula:** `on_time_delivery_rate_pct` (stored column)
- **Required columns:** `Suppliers.supplier_id`, `Suppliers.on_time_delivery_rate_pct`
- **Grouping level:** `supplier_id`
- **Baseline / Current:** **not separable** — the column has no period split. Reference values: S001 = **88%**, S002 = **97%**, S003 = **95%**
- **% change:** `null` + flag `no_period_split`
- **Anomaly:** `value < TH_OTD_MIN_PCT (90%)` → **S001 (88%) → ANOMALY**; S002/S003 normal.

**(b) Derived rate from purchase orders (period-splittable)**
- **Formula:** `otd_pct = COUNT(supplier_lead_days <= expected_lead_time_days) / COUNT(*) * 100`, per supplier per period
- **Required columns:** `Purchase_Orders.supplier_id`, `Purchase_Orders.request_date`, `Purchase_Orders.supplier_lead_days`, `Suppliers.expected_lead_time_days`
- **Grouping level:** `supplier_id` × period
- **Baseline:** S001 = **100.0%** (3/3) · S002 = **100.0%** (3/3) · S003 = **100.0%** (3/3)
- **Current:** S001 = **0.0%** (0/3) · S002 = **100.0%** (3/3) · S003 = **100.0%** (2/2)
- **% change:** use `PP_CHANGE` — S001 = **−100.00 pp** · S002 = 0.00 pp · S003 = 0.00 pp
- **Anomaly:** `otd_pct < 90%` or `pp_change <= −10 pp` → **S001 → ANOMALY**
- **Consistency note:** across all periods S001's derived OTD is 50% (3 of 6 POs on time), while the stored reported rate is 88% — a **38 pp gap**. The two figures use different definitions and windows, so the discrepancy must be surfaced as a flag (`reported_vs_derived_gap_pp = 38.0`), not reconciled silently. (S002 gap = −3.0 pp, S003 gap = −5.0 pp.)

---

## 5. CUSTOMER ANALYSIS

`Customer_Feedback` has **no `order_id`**, so every rate below is expressed **per feedback record**, not per order. A per-order denominator is only reachable by an indirect join on `product_id` + `date`, which is an approximation and must be labelled as such if used.

### M23 · Complaint count
- **Formula:** `COUNT(*) WHERE complaint_type NOT IN ('None', '', NULL)`
- **Required columns:** `Customer_Feedback.date`, `Customer_Feedback.complaint_type`
- **Grouping level:** period; also `product_id` × period and `complaint_type` × period
- **Baseline:** **10** complaints (out of 35 feedback records)
- **Current:** **10** complaints (out of 23 feedback records)
- **% change:** **0.00%** (Δ 0)
- **Anomaly:** `pct_change >= 20%` **or** `delta >= 3` → **no anomaly** on the raw count. Note the deliberate trap: the count is flat while the *rate* rises (M24) — the two must never be substituted for each other.

### M24 · Complaint rate
- **Formula:** `complaint_count / feedback_records * 100` per period
- **Required columns:** `Customer_Feedback.date`, `Customer_Feedback.complaint_type`
- **Grouping level:** period
- **Baseline:** `10 / 35` = **28.57%**
- **Current:** `10 / 23` = **43.48%**
- **% change:** **+14.91 pp** via `PP_CHANGE` (the relative change is `+52.17%`; both must be emitted, with the pp figure as primary)
- **Anomaly:** `pp_change >= TH_COMPLAINT_RATE_PP (5 pp)` → **ANOMALY (+14.91 pp)**

### M25 · Refund rate
- **Formula:** `COUNT(refund == 'Yes') / feedback_records * 100`
- **Required columns:** `Customer_Feedback.date`, `Customer_Feedback.refund`
- **Grouping level:** period
- **Baseline:** `0 / 35` = **0.00%**
- **Current:** `1 / 23` = **4.35%**
- **% change:** `null` + `base_zero = true`; report `PP_CHANGE = +4.35 pp`
- **Anomaly:** `current_count > 0` while `baseline_count == 0` (new occurrence) → **ANOMALY**

### M26 · Cancellation rate
- **Formula:** `COUNT(order_cancelled == 'Yes') / feedback_records * 100`
- **Required columns:** `Customer_Feedback.date`, `Customer_Feedback.order_cancelled`
- **Grouping level:** period
- **Baseline:** `0 / 35` = **0.00%**
- **Current:** `3 / 23` = **13.04%**
- **% change:** `null` + `base_zero = true`; report `PP_CHANGE = +13.04 pp`
- **Anomaly:** `current_count > 0` while `baseline_count == 0` → **ANOMALY**
- **Denominator note:** because there is no `order_id`, this is cancellations *per feedback record*, which is not the same as cancellations per order. Flag `denominator = 'feedback_records'`.

### M27 · Average customer rating
- **Formula:** `AVG(rating)` per period (ratings take the values 3, 3.5, 4, 4.5, 5)
- **Required columns:** `Customer_Feedback.date`, `Customer_Feedback.rating`
- **Grouping level:** period; also `product_id` × period
- **Baseline:** **4.443** (n = 35)
- **Current:** **4.283** (n = 23)
- **% change:** **−3.61%**; Δ = **−0.160**
- **Anomaly:** `delta <= TH_RATING_DELTA (−0.25)` → **no anomaly on the threshold**, but flag `direction = 'down'` and report the sample size, since n drops from 35 to 23 and the mean is unweighted. Emit the full rating histogram alongside so a distribution shift is visible even when the mean barely moves.

### M28 · Change in complaint type
- **Formula:** per `complaint_type` — `count` per period, `share_pct = count / complaint_count * 100` per period, `count_delta = cur − base`, `share_pp_change = cur_share − base_share`
- **Required columns:** `Customer_Feedback.date`, `Customer_Feedback.complaint_type`
- **Grouping level:** `complaint_type` × period
- **Baseline:** Delivery Delay 7 (70.0%) · Product Quality 2 (20.0%) · Packaging 1 (10.0%) · Out of Stock 0 (0.0%)
- **Current:** Out of Stock **5 (50.0%)** · Product Quality 3 (30.0%) · Delivery Delay **1 (10.0%)** · Packaging 1 (10.0%)
- **% change:** Delivery Delay **−60.0 pp** (Δ −6) · Out of Stock **+50.0 pp** (Δ +5) · Product Quality **+10.0 pp** (Δ +1) · Packaging **0.0 pp** (Δ 0)
- **Anomaly:** `abs(share_pp_change) >= TH_COMPLAINT_TYPE_PP (20 pp)` → **Delivery Delay (−60 pp) and Out of Stock (+50 pp) → ANOMALY**. Also flag any type that goes from `0` occurrences to `> 0` (`Out of Stock`) — a new category is always reportable regardless of share.

---

## 6. Reference values (machine-computed)

Produced by `rootiq_metrics.py`. Full precision is in `rootiq_metric_reference_values.json`; the table below is rounded for reading.

| ID | Metric | Baseline | Current | Δ | Δ% | Anomaly |
|---|---|---|---|---|---|---|
| M01 | Total revenue | 39,975.00 | 32,660.00 | −7,315.00 | −18.30% | YES |
| M02 | Revenue % change | — | — | −7,315.00 | −18.30% | YES |
| M03 | Revenue by product | P1 30,310 / P2 5,940 / P3 3,725 | P1 22,680 / P2 6,180 / P3 3,800 | — | — | YES (P1) |
| M04 | Revenue % change by product | — | — | P1 −7,630 / P2 +240 / P3 +75 | P1 −25.17% / P2 +4.04% / P3 +2.01% | YES (P1) |
| M05 | Units sold by product | P1 433 / P2 198 / P3 149 | P1 324 / P2 206 / P3 152 | — | — | YES (P1) |
| M06 | Units-sold % change | 780 total | 682 total | −98 | −12.56% (P1 −25.17%) | YES |
| M07a | Unit price per product | 70 / 30 / 25 | 70 / 30 / 25 | 0 | 0.00% | no |
| M07b | Blended avg price | 51.25 | 47.89 | −3.36 | −6.56% | no (mix) |
| M08 | Contribution to decline | — | — | — | P1 +104.31% / P2 −3.28% / P3 −1.03% | YES (P1) |
| M09 | Ranking by negative impact | — | — | — | 1 P001 / 2 P003 / 3 P002 | YES |
| M10 | Total stockout hours | P1 0 / P2 0 / P3 0 | P1 86.6 / P2 0 / P3 0 | +86.6 | null (base 0) | YES (P1) |
| M11 | Avg stockout hours | 0.000 | P1 3.093 | +3.093 | null (base 0) | YES (P1) |
| M12 | Stockout days | 0 | P1 8 | +8 | null (base 0) | YES (P1) |
| M13 | Closing-stock trend (avg) | P1 119.11 / P2 140.39 / P3 113.93 | P1 47.07 / P2 214.32 / P3 196.86 | — | P1 −60.48% / P2 +52.66% / P3 +72.79% | YES (P1) |
| M14 | Availability | 100.00% all | P1 87.11% / P2 100% / P3 100% | −12.89 pp | — | YES (P1) |
| M15 | Avg PO approval time | 0.444 d | 3.250 d | +2.806 d | +631.25% | YES |
| M16 | Approval time by product | P1 0.667 / P2 0.333 / P3 0.333 | P1 7.667 / P2 0.667 / P3 0.500 | P1 +7.000 | P1 +1050% | YES (P1) |
| M17 | Avg supplier lead time | 3.333 d | 4.000 d | +0.667 d | +20.00% | YES |
| M18 | Delivery delays (mean) | 0.000 d | 0.750 d | +0.750 d | null (base 0) | YES |
| M19 | Abnormal POs | 0 | 3 (PO004/5/6) | +3 | null (base 0) | YES |
| M20 | Supplier lead-time change | 3 / 3 / 4 | 5 / 3 / 4 | S001 +2 d | S001 +66.67% | YES (S001) |
| M21 | Unit-cost change | 34 / 14 / 11 | 34.5 / 14 / 11.2 | S001 +0.50, S003 +0.20 | +1.47% / +1.82% | YES (small) |
| M22a | OTD (reported) | n/a | S001 88% / S002 97% / S003 95% | — | no split | YES (S001) |
| M22b | OTD (derived) | 100% / 100% / 100% | S001 0% / S002 100% / S003 100% | S001 −100 pp | — | YES (S001) |
| M23 | Complaint count | 10 / 35 records | 10 / 23 records | 0 | 0.00% | no |
| M24 | Complaint rate | 28.57% | 43.48% | +14.91 pp | +52.17% rel | YES |
| M25 | Refund rate | 0.00% | 4.35% | +4.35 pp | null (base 0) | YES |
| M26 | Cancellation rate | 0.00% | 13.04% | +13.04 pp | null (base 0) | YES |
| M27 | Avg rating | 4.443 | 4.283 | −0.160 | −3.61% | no (watch) |
| M28 | Complaint-type mix | DD 70% / PQ 20% / PK 10% | OOS 50% / PQ 30% / DD 10% / PK 10% | DD −6, OOS +5 | DD −60 pp, OOS +50 pp | YES |

---

## 7. Schema constraints that constrain these calculations

These are carried forward from the schema-validation layer and are **hard limits on what can be computed**, not bugs to be worked around silently.

| # | Constraint | Metrics affected | Handling |
|---|---|---|---|
| 1 | `Suppliers` has no date column — only `baseline_*` / `current_*` pairs | M20, M21, M22a | Compute as a two-point change; flag `no_period_split`; corroborate against PO-derived values where possible |
| 2 | `Customer_Feedback` has no `order_id` | M23–M26 | Rates use `feedback_records` as denominator; flag `denominator = 'feedback_records'` |
| 3 | `order_id` and `po_id` are isolated primary keys (nothing references them) | M01–M09, M15–M19 | No order-to-PO linkage exists; PO metrics and sales metrics cannot be joined at row level |
| 4 | `Inventory.received` has no `po_id` | M10–M14 | Receipts cannot be attributed to a purchase order; do not attempt a receipt-to-PO reconciliation |
| 5 | `Sales` has no `supplier_id` | M03–M09 | Supplier attribution must pass through `product_id` → `Suppliers`, which is 1:1 so it is lossless |
| 6 | `Suppliers` is 1:1 supplier↔product | M20–M22 | Supplier-level and product-level metrics are numerically interchangeable here; do not generalise that assumption |
| 7 | `PO006` falls outside both periods | M15–M19 | Included in `CURRENT` under the `request_date` rule (2026-09-20); its `delivery_date` is `OUTSIDE`. Emit both classifications and never let one silently override the other |
| 8 | Baseline is `0` for stockouts, delays, refunds, cancellations | M10–M12, M18, M19, M25, M26 | `PCT_CHANGE` must return `null` + `base_zero = true`; report absolute deltas instead |

---

## 8. Implementation contract

### 8.1 Output shape
Every metric is emitted as one flat record so the investigator layer can consume a uniform table:

```json
{
  "metric_id": "M01",
  "metric_name": "total_revenue",
  "group": {"period": null, "product_id": null, "supplier_id": null},
  "value_baseline": 39975.0,
  "value_current": 32660.0,
  "delta": -7315.0,
  "pct_change": -18.2989,
  "pp_change": null,
  "is_anomaly": true,
  "threshold_used": 10.0,
  "flags": []
}
```

### 8.2 Required flags
`base_zero`, `no_rows`, `no_period_split`, `small_base`, `mix_affected`, `denominator`, `cost_granularity`, `reported_vs_derived_gap`, `period_conflict` (a row assigned to different periods by different date columns).

### 8.3 Determinism checklist
1. Period windows are inclusive constants, never derived from the data.
2. All sorts specify a full tie-break key.
3. `PCT_CHANGE` never divides by zero and never fabricates a value.
4. Outliers are reported, never removed.
5. No imputation anywhere.
6. Assert the data-quality identities on every run: `revenue == quantity * unit_price`; `closing_stock == opening_stock + received - sold`; `approval_days == approval_date - request_date`; `supplier_lead_days == delivery_date - order_date`; `request <= approval <= order <= delivery`. A failed assertion must raise, not warn.

### 8.4 Execution order
`load → validate identities → tag periods → compute M01–M28 → attach flags → serialise`. The investigator layer must receive the serialised output only; it never reads the raw workbook.

---

## 9. Explicitly out of scope

Per the brief, this specification contains **no root-cause reasoning** and **no business recommendations**. The metrics above describe *what changed and by how much*; they do not assert *why*, and they do not rank remedies. Correlation between M01–M28 is a downstream concern and must be computed by a separate layer.
