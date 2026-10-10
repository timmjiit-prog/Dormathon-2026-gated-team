# RootIQ — Dataset Inspection & Schema Validation Report

**Workbook:** `RootIQ_SME_Dataset_Scenario1.xlsx`  
**Scope:** Factual data-inspection layer only. No root-cause analysis, no business recommendations, no assumptions.  
**Periods referenced:** BASELINE = 2026-08-03 → 2026-08-30 · CURRENT / PROBLEM = 2026-08-31 → 2026-09-27  
**Method:** read-only inspection of the live workbook. No cell was modified.

---

## 0. Sheet inventory (actual vs. expected)

| # | Sheet               | Role                                                  | Rows (data) | Cols |
| - | ------------------- | ----------------------------------------------------- | ----------- | ---- |
| 1 | `Guide`             | **Metadata / documentation sheet** (not a data table) | —           | —    |
| 2 | `Sales`             | Fact table                                            | 322         | 7    |
| 3 | `Inventory`         | Fact table                                            | 168         | 8    |
| 4 | `Purchase_Orders`   | Fact table                                            | 17          | 11   |
| 5 | `Suppliers`         | Dimension table                                       | 3           | 10   |
| 6 | `Customer_Feedback` | Fact table                                            | 58          | 7    |

- The workbook contains **6 sheets, not 5**. `Guide` was not listed in the request. It is a descriptive sheet documenting each table's purpose, primary key, join fields and declared row counts.
- `Guide`'s declared row counts match the measured counts exactly: Sales 322 / Inventory 168 / Purchase_Orders 17 / Suppliers 3 / Customer_Feedback 58.
- Total data rows across the five data tables: **568**.

---

## A. Dataset schema

### A.1 `Sales` — fact table, grain = one order (`order_id`)

| Column         | Type (inferred)            | Notes                                           |
| -------------- | -------------------------- | ----------------------------------------------- |
| `date`         | number (Excel serial date) | sale date                                       |
| `order_id`     | text                       | format `O0001`                                  |
| `product_id`   | text                       | `P001` / `P002` / `P003`                        |
| `product_name` | text                       | redundant label                                 |
| `quantity`     | number (integer)           | units sold                                      |
| `unit_price`   | number                     | constant per product: P001=70, P002=30, P003=25 |
| `revenue`      | number                     | = quantity × unit_price                         |

- **Primary key:** `order_id` (322 rows / 322 distinct → unique).
- **Foreign keys:** `product_id` → `Suppliers.product_id`.

### A.2 `Inventory` — fact table, grain = one day × one product

| Column           | Type (inferred)            | Notes                                       |
| ---------------- | -------------------------- | ------------------------------------------- |
| `date`           | number (Excel serial date) | snapshot date                               |
| `product_id`     | text                       | `P001` / `P002` / `P003`                    |
| `product_name`   | text                       | redundant label                             |
| `opening_stock`  | number                     | 8 rows equal 0                              |
| `received`       | number                     | 16 rows non-zero                            |
| `sold`           | number                     | units out                                   |
| `closing_stock`  | number                     | 8 rows equal 0                              |
| `stockout_hours` | number                     | only 4 distinct values: 0 / 3.4 / 11.2 / 12 |

- **Primary key:** composite `date` + `product_id` (168 rows, no duplicate combination).
- **Foreign keys:** `product_id` → `Suppliers.product_id`.

### A.3 `Purchase_Orders` — fact table, grain = one purchase order (`po_id`)

| Column               | Type (inferred)            | Notes                            |
| -------------------- | -------------------------- | -------------------------------- |
| `po_id`              | text                       | `PO001` …                        |
| `product_id`         | text                       | FK                               |
| `supplier_id`        | text                       | FK, `S001` …                     |
| `request_date`       | number (Excel serial date) |                                  |
| `approval_date`      | number (Excel serial date) |                                  |
| `order_date`         | number (Excel serial date) |                                  |
| `delivery_date`      | number (Excel serial date) |                                  |
| `quantity`           | number                     | ordered units                    |
| `status`             | text                       | `Delivered` / `Pending Delivery` |
| `approval_days`      | number                     | derived                          |
| `supplier_lead_days` | number                     | derived                          |

- **Primary key:** `po_id` (17 / 17 distinct → unique).
- **Foreign keys:** `product_id` → `Suppliers.product_id`; `supplier_id` → `Suppliers.supplier_id`.

### A.4 `Suppliers` — dimension table, grain = one supplier (1:1 with product)

| Column                      | Type (inferred) | Notes                              |
| --------------------------- | --------------- | ---------------------------------- |
| `supplier_id`               | text            | PK                                 |
| `supplier_name`             | text            |                                    |
| `product_id`                | text            | also unique → 1:1 supplier↔product |
| `product_name`              | text            | redundant label                    |
| `expected_lead_time_days`   | number          | contracted lead time               |
| `baseline_avg_lead_days`    | number          |                                    |
| `current_avg_lead_days`     | number          |                                    |
| `baseline_unit_cost`        | number          |                                    |
| `current_unit_cost`         | number          |                                    |
| `on_time_delivery_rate_pct` | number          | percent                            |

- **Primary key:** `supplier_id` (3 / 3 distinct). `product_id` is also unique.
- **Referenced by:** `Sales`, `Inventory`, `Purchase_Orders`, `Customer_Feedback` via `product_id`; `Purchase_Orders` also via `supplier_id`.
- **No date / period column** — see issue P0-1.

### A.5 `Customer_Feedback` — fact table, grain = one feedback record (`feedback_id`)

| Column            | Type (inferred)            | Notes        |
| ----------------- | -------------------------- | ------------ |
| `date`            | number (Excel serial date) |              |
| `feedback_id`     | text                       | `F001` …     |
| `product_id`      | text                       | FK           |
| `complaint_type`  | text                       | category     |
| `rating`          | number                     | score        |
| `refund`          | text                       | `No` / `Yes` |
| `order_cancelled` | text                       | `No` / `Yes` |

- **Primary key:** `feedback_id` (58 / 58 distinct → unique).
- **Foreign keys:** `product_id` → `Suppliers.product_id`. **No `order_id`** — see issue P1-3.

---

## B. Data-quality report

### B.1 Missing values — none

| Sheet             | Columns | Missing cells | Missing rate |
| ----------------- | ------- | ------------- | ------------ |
| Sales             | 7       | 0             | 0%           |
| Inventory         | 8       | 0             | 0%           |
| Purchase_Orders   | 11      | 0             | 0%           |
| Suppliers         | 10      | 0             | 0%           |
| Customer_Feedback | 7       | 0             | 0%           |

No blank cells, and no `N/A` / `-` / `null` placeholders in any of the 43 columns.

### B.2 Duplicate rows — none

| Sheet             | Fully duplicated rows | Primary-key duplicates |
| ----------------- | --------------------- | ---------------------- |
| Sales             | 0                     | 0                      |
| Inventory         | 0                     | 0                      |
| Purchase_Orders   | 0                     | 0                      |
| Suppliers         | 0                     | 0                      |
| Customer_Feedback | 0                     | 0                      |

### B.3 Invalid dates — none

| Sheet             | Date column(s)  | Non-numeric | Illegal serial | Observed range          |
| ----------------- | --------------- | ----------- | -------------- | ----------------------- |
| Sales             | `date`          | 0           | 0              | 2026-08-03 → 2026-09-27 |
| Inventory         | `date`          | 0           | 0              | 2026-08-03 → 2026-09-27 |
| Purchase_Orders   | `request_date`  | 0           | 0              | 2026-08-03 → 2026-09-23 |
| Purchase_Orders   | `approval_date` | 0           | 0              | 2026-08-03 → 2026-09-28 |
| Purchase_Orders   | `order_date`    | 0           | 0              | 2026-08-03 → 2026-09-28 |
| Purchase_Orders   | `delivery_date` | 0           | 0              | 2026-08-06 → 2026-10-03 |
| Customer_Feedback | `date`          | 0           | 0              | 2026-08-03 → 2026-09-27 |

All dates are valid Excel date serials. No text-formatted dates, no impossible values.

**Records falling outside the two analysis periods — exactly 1:** `Purchase_Orders` row `PO006` (`approval_date` / `order_date` = 2026-09-28, `delivery_date` = 2026-10-03), i.e. past the CURRENT period end (2026-09-27); `status` = `Pending Delivery`.

Records inside each period:

| Sheet (date column)               | In BASELINE | In CURRENT | Outside both |
| --------------------------------- | ----------- | ---------- | ------------ |
| Sales (`date`)                    | 163         | 159        | 0            |
| Inventory (`date`)                | 84          | 84         | 0            |
| Customer_Feedback (`date`)        | 35          | 23         | 0            |
| Purchase_Orders (`request_date`)  | 9           | 8          | 0            |
| Purchase_Orders (`approval_date`) | 9           | 7          | 1 (PO006)    |
| Purchase_Orders (`delivery_date`) | 8           | 8          | 1 (PO006)    |

There are no records earlier than 2026-08-03 and no gap between the two periods.

### B.4 Invalid numeric values — none

- **Non-numeric values in numeric columns: 0.** No text or corrupted values mixed in.
- **Negative values: 0.** Applies to `quantity`, `revenue`, all stock fields, `stockout_hours`, `approval_days`, `supplier_lead_days`, `rating`, and all cost/lead-time fields.
- **Statistical outliers (IQR ×1.5 — flagged as facts, not as errors):**

| Sheet           | Column           | Outlier count | Example values       |
| --------------- | ---------------- | ------------- | -------------------- |
| Sales           | `quantity`       | 22            | 16, 14, 14, 16, 13   |
| Sales           | `revenue`        | 47            | 560, 1120, 630, 980  |
| Sales           | `unit_price`     | 0             | constant per product |
| Inventory       | `received`       | 16            | 145, 100, 90, 135    |
| Inventory       | `stockout_hours` | 8             | 11.2, 12, 12         |
| Purchase_Orders | `approval_days`  | 3             | 7, 8, 8              |

- **Internal identity checks — all pass with 0 violations:**
  - `Sales`: `revenue = quantity × unit_price` → 0 mismatches
  - `Inventory`: `closing_stock = opening_stock + received − sold` → 0 mismatches
  - `Purchase_Orders`: `approval_days = approval_date − request_date` → 0 mismatches
  - `Purchase_Orders`: `supplier_lead_days = delivery_date − order_date` → 0 mismatches
  - `Purchase_Orders`: date order `request ≤ approval ≤ order ≤ delivery` → 0 violations

### B.5 Other data-quality observations (factual)

1. `Suppliers` has **no date/period column** — only paired `baseline_*` and `current_*` fields, with nothing in the data declaring which calendar window "current" covers.
2. `product_name` is **redundantly stored** in `Sales`, `Inventory` and `Suppliers`. Current mapping is consistent (P001→Product A, P002→Product B, P003→Product C) with 0 conflicts.
3. `Inventory` has 8 rows each with `opening_stock` = 0 and `closing_stock` = 0; `stockout_hours` takes only 4 distinct values (0 / 3.4 / 11.2 / 12).
4. `Suppliers` is strictly **1:1 supplier↔product** (S001→P001, S002→P002, S003→P003), so it cannot express a supplier carrying multiple products.
5. `Guide` is a metadata sheet and must be excluded from the analysis layer, otherwise it will be counted as a data table.

---

## C. Relationship map

```
                        ┌───────────────────────────┐
                        │   Suppliers  (dim, 3)     │
                        │   PK: supplier_id         │
                        │   product_id (1:1)        │
                        └────────────┬──────────────┘
        product_id                   │ product_id        supplier_id
   ┌──────────────┬──────────────────┼───────────────┬──────────────────┐
   ▼              ▼                  ▼               ▼                  ▼
┌────────┐  ┌───────────┐  ┌──────────────────┐  ┌────────────────────┐
│ Sales  │  │ Inventory │  │ Purchase_Orders  │  │ Customer_Feedback  │
│  322   │  │    168    │  │       17         │  │        58          │
│PK:order│  │PK:date+pid│  │   PK: po_id      │  │ PK: feedback_id    │
│  _id   │  │           │  │                  │  │                    │
└────────┘  └───────────┘  └──────────────────┘  └────────────────────┘
   date        date        request/approval/         date
                            order/delivery_date
   (the four fact tables share a date axis but have no direct foreign key between them)
```

### C.1 Table roles

| Sheet               | Type      | Grain                                                   |
| ------------------- | --------- | ------------------------------------------------------- |
| `Sales`             | Fact      | one row = one order (`order_id`)                        |
| `Inventory`         | Fact      | one row = one day × one product (`date` + `product_id`) |
| `Purchase_Orders`   | Fact      | one row = one purchase order (`po_id`)                  |
| `Customer_Feedback` | Fact      | one row = one feedback record (`feedback_id`)           |
| `Suppliers`         | Dimension | one row = one supplier (which also pins one product)    |


### C.2 Join keys, cardinality and referential integrity

| Join key      | Parent                        | Child                                                   | Cardinality | Referential integrity                                                                                                                           |
| ------------- | ----------------------------- | ------------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `product_id`  | `Suppliers` (P001/P002/P003)  | Sales, Inventory, Purchase_Orders, Customer_Feedback    | 1 : N       | PASS — 0 orphan values                                                                                                                          |
| `supplier_id` | `Suppliers` (S001/S002/S003)  | Purchase_Orders                                         | 1 : N       | PASS — 0 orphan values                                                                                                                          |
| `order_id`    | `Sales` (322 unique)          | — nothing references it                                 | 1 : 0       | **Isolated PK**                                                                                                                                 |
| `po_id`       | `Purchase_Orders` (17 unique) | — nothing references it                                 | 1 : 0       | **Isolated PK**                                                                                                                                 |
| `date`        | — no shared date dimension    | Sales / Inventory / Customer_Feedback / Purchase_Orders | —           | No calendar dimension; each table's date means something different (sale day / stock day / feedback day / request-approval-order-delivery days) |

**Orphan checks (foreign keys not found in the target table):**

- `Sales.product_id` not in `Suppliers`: **0**
- `Inventory.product_id` not in `Suppliers`: **0**
- `Purchase_Orders.product_id` not in `Suppliers`: **0**
- `Purchase_Orders.supplier_id` not in `Suppliers`: **0**
- `Customer_Feedback.product_id` not in `Suppliers`: **0**

**Key uniqueness:** `order_id` 322/322, `po_id` 17/17, `supplier_id` 3/3, `feedback_id` 58/58 — all 1:1.  
**`product_name` consistency:** P001→Product A, P002→Product B, P003→Product C is identical in every table that carries the field (0 conflicts).

---

## D. Issues to fix before analysis

### P0 — blocking (period comparison is not well-defined until resolved)

1. **`Suppliers` has no period column.** Sheet `Suppliers` has no `date` / `period` field, only paired `baseline_*` and `current_*` columns. All 3 rows affected. Example: S001 `baseline_avg_lead_days`=3 / `current_avg_lead_days`=5. The data does not state whether "current" means 2026-08-31 → 2026-09-27, so the period definition cannot be verified from the data.
2. **`Purchase_Orders` contains 1 record beyond the CURRENT period end.** `PO006`: `approval_date`=2026-09-28, `order_date`=2026-09-28, `delivery_date`=2026-10-03, `status`=`Pending Delivery`. An explicit include/exclude rule is needed.

### P1 — structural (limits joinability)

1. **`Customer_Feedback` cannot be linked to an order.** It has `product_id` but no `order_id`. All 58 rows affected. Feedback / refund / cancellation can only be aligned to `Sales` indirectly via `product_id` + `date`.
2. **`Inventory.received` has no key link to `Purchase_Orders`.** `Inventory` has no `po_id`, and `po_id` is not referenced anywhere. 168 Inventory rows (16 with non-zero `received`) and 17 Purchase_Orders rows affected. Receipts cannot be attributed to a specific purchase order.
3. **`Sales` has no supplier dimension.** `Sales` carries only `product_id`, no `supplier_id`. All 322 rows affected. Sales-to-supplier attribution must go through `product_id` → `Suppliers`.

### P2 — redundancy / drift risk (currently consistent)

1. **`product_name` is stored redundantly in 4 places** (`Sales` 322 + `Inventory` 168 + `Suppliers` 3 = 493 redundant values; `Purchase_Orders` stores only `product_id`). Currently 0 conflicts; any future single-table rename would create inconsistency immediately.
2. **`Suppliers` is 1:1 supplier↔product** (3 rows: S001→P001, S002→P002, S003→P003) and cannot model a supplier carrying multiple products.
3. **`Guide` must be excluded from the analysis layer** so it is not counted as a data table.

### P3 — statistical outliers (facts only, do NOT treat as dirty data)

1. IQR outliers: `Sales.quantity` 22, `Sales.revenue` 47, `Inventory.received` 16, `Inventory.stockout_hours` 8, `Purchase_Orders.approval_days` 3. Examples: quantity 16/14; received 145/135/100; stockout_hours 11.2/12; approval_days 7/8. All sit inside plausible business ranges (no negatives, no non-numeric values) and are therefore more likely genuine high-value events than entry errors.

---

## Overall data-quality verdict (factual)

- **Structurally very clean:** 0 missing values, 0 duplicate rows, 0 primary-key duplicates, 0 invalid dates, 0 non-numeric values, 0 negative values.
- **Internal consistency: 100% pass** — Sales revenue identity, Inventory stock identity, and all Purchase_Orders day-count / date-order checks return 0 errors.
- **Referential integrity: 100% pass** — no orphan values on `product_id` or `supplier_id`.
- **The real gaps are missing join keys and an undefined period definition, not dirty data:** `order_id` and `po_id` are isolated primary keys; `Customer_Feedback` lacks `order_id`; `Inventory` cannot link receipts to purchase orders; `Sales` lacks `supplier_id`; `Suppliers` has no period column; and 1 Purchase_Orders row (PO006) sits outside the CURRENT period.
