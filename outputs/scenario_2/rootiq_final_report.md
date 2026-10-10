# RootIQ Investigation Report

**Case ID:** scenario_2
**Investigation Date:** 2026-10-10
**Engine:** RootIQ Autonomous Root Cause Investigator v1.0.0

---

## Executive Summary

Gross profit declined 16.93% (20,120 to 16,713) and gross margin fell 8.81pp (53.02% to 44.21%) while revenue remained broadly stable (-0.37%, 37,945 to 37,805). The validated root cause is a Supplier Cost Increase -- S002's unit cost rose 33.33% (30 to 40), exactly matching P002's sales unit cost increase, driving P002 COGS +32.08% and P002 gross profit -33.96%. Confidence is HIGH. The highest-priority action is to investigate S002's unit cost increase and negotiate or seek alternative supply within 72 hours.

## Business Problem

Why did gross profit and gross margin fall even though revenue remained broadly stable?

## Investigation Period

**Baseline:** 2026-08-03 to 2026-08-30 (28 days)
**Current:** 2026-08-31 to 2026-09-27 (28 days)

## Key Metrics

| Metric | Baseline | Current | Change |
|---|---|---|---|
| Revenue | 37,945 | 37,805 | -0.37% (stable) |
| COGS | 17,825 | 21,091.7 | +18.33% |
| Gross profit | 20,120 | 16,713.3 | -16.93% |
| Gross margin | 53.02% | 44.21% | -8.81pp |
| P002 unit cost | 30 | 40 | +33.33% |
| P002 COGS | 9,600 | 12,680 | +32.08% |
| P002 gross profit | 9,600 | 6,340 | -33.96% |
| P002 gross margin | 50.0% | 33.33% | -16.67pp |
| P002 contribution to decline | -- | -- | 128.57% |
| S002 unit cost | 30 | 40 | +33.33% |
| All selling prices | Unchanged | Unchanged | 0% |
| Inventory stockout hours | 0 | 0 | 0 |
| PO approval time | 0.56 days | 0.33 days | -40% (improved) |
| Supplier lead time | 3.33 days | 3.33 days | 0% |
| Late PO orders | 0 | 0 | 0 |
| Complaint rate | 7.14% | 21.43% | +200% |

## Ranked Hypotheses

| Rank | Hypothesis | Confidence | Supporting Evidence | Contradicting Evidence |
|---|---|---|---|---|
| 1 | Supplier cost increase (S002 driving P002 unit cost inflation) | HIGH | S002 unit cost +33.33% (30->40); P002 unit cost +33.33% (30->40) matching exactly; P002 COGS +32.08%; P002 GP -33.96%; P002 margin -16.67pp; P002 contribution 128.57% | None identified |
| 2 | Product-specific cost issue (P002 only) | HIGH | P002 +33.33% vs P001 +2.5% and P003 +1.33%; P002 margin -16.67pp vs P001 -1.11pp and P003 -0.57pp | Root cause of S002-specific increase requires supplier investigation |
| 3 | Revenue or price decline causing profit drop | LOW | Revenue slightly declined 0.37% | All prices unchanged; 0.37% cannot explain 16.93% GP decline; P003 revenue grew +2.62% |
| 4 | Inventory shortage or stockout impact | LOW | -- | 0 stockout hours; 100% availability; closing stock increased for all products |

## Root Cause Chain

```
Observed Problem: Gross profit declined 16.93% (20,120 -> 16,713)
      ↓
Contributing Factor: P002 gross profit declined 33.96% (128.57% of total decline)
      ↓
Intermediate Cause: P002 COGS increased 32.08% (9,600 -> 12,680) with zero price change
      ↓
Underlying Cause: P002 unit cost increased 33.33% (30 -> 40) with all selling prices unchanged
      ↓
Validated Root Cause: S002 supplier unit cost increased 33.33% (30 -> 40)
      [Confidence: HIGH]
```

## Supporting Evidence

1. S002 unit cost increased 33.33% (30 to 40) -- exact match to P002 sales unit cost
2. P002 COGS increased 32.08% (9,600 to 12,680)
3. P002 gross profit declined 33.96% (9,600 to 6,340)
4. P002 gross margin declined 16.67pp (50% to 33.33%)
5. P002 accounts for 128.57% of total gross profit decline
6. All selling prices unchanged across all products (P001 45, P002 60, P003 35)
7. P001 unit cost only +2.5% (20 to 20.5) and P003 +1.33% (15 to 15.2) -- confirms product-specific scope
8. Revenue stable at -0.37% -- the problem is cost-side, not revenue-side

## Contradicting Evidence

1. All selling prices were unchanged, ruling out a pricing problem as the cause
2. Revenue decline of 0.37% cannot explain gross profit decline of 16.93%
3. P003 revenue grew +2.62% with gross profit growing +1.59%
4. All products had 0 stockout hours and 100% availability, ruling out inventory issues
5. Closing stock increased for all products (P001 +12.9%, P002 +27.02%, P003 +33.37%)
6. PO approval time improved -40% and supplier lead time unchanged at 3.33 days, ruling out procurement issues

## Self-Disproof Result

- **Leading hypothesis tested:** Supplier cost increase (S002 driving P002 unit cost inflation)
- **Survived challenge:** YES
- **Control products:** P001 unit cost +2.5% and P003 unit cost +1.33% (minimal) vs P002 +33.33% (severe) -- confirms product-specific scope
- **Alternative: Revenue/price decline:** Contradicted -- all prices unchanged, 0.37% revenue change cannot explain 16.93% profit decline
- **Alternative: Inventory shortage:** Contradicted -- 0 stockout hours, 100% availability, increasing closing stock
- **Missing evidence:** Reason for S002 unit cost increase requires supplier investigation; whether temporary or permanent is unknown
- **Stronger alternative found:** NO

Note: The formal 5-dimension self-disproof module was not executed for this scenario. The above assessment is based on the specialist investigator's hypothesis evaluation.

## Evidence Validation

- **Validator status:** Not recorded
- **Confidence:** HIGH (investigator-level)
- **Questionable claims:** Not recorded
- **Required corrections:** Not recorded

Note: The formal 8-check Evidence Validator was not executed for this scenario. The root cause identification is based on the specialist investigator's HIGH-confidence hypothesis evaluation.

## Business Impact

| Metric | Value | Type |
|---|---|---|
| Total gross profit loss | 3,406.7 | EXACT |
| Gross profit decline percentage | -16.93% | EXACT |
| Gross margin decline | -8.81pp | EXACT |
| P002 gross profit loss | 3,260 | EXACT |
| P002 contribution to decline | 128.57% | EXACT |
| COGS increase | 3,266.7 | EXACT |

## Immediate Corrective Action

Investigate S002's unit cost increase (30 to 40, +33.33%) -- determine whether the increase is temporary or permanent, negotiate pricing, or qualify an alternative supplier for P002. Owner: Purchasing Manager. Deadline: 72 hours.

Note: This action is derived from the investigator's recommended next investigation, not from a formal Corrective Action Executor run.

## Preventive Action

Implement supplier cost monitoring with alerts when any supplier unit cost changes exceed 10%. Establish dual-sourcing for P002 to reduce dependency on S002.

Note: Not generated by the formal Corrective Action Executor.

## Monitoring KPI

| KPI | Normal Range | Warning Threshold | Critical Threshold |
|---|---|---|---|
| P002 unit cost | <= 30 | > 30 (+10%) | > 35 (+16.7%) |
| S002 unit cost | <= 30 | > 30 | > 35 |
| Gross margin (overall) | > 50% | < 48% | < 45% |
| P002 gross margin | > 45% | < 40% | < 35% |

Note: Monitoring KPIs are derived from the verified metrics, not from a formal Corrective Action Executor run.

## Action Register

Not recorded. The Corrective Action Executor was not run for this scenario. The investigator recommended next investigation domain: Supplier.

## Limitations / Missing Evidence

1. The formal 8-check Evidence Validator was not executed -- root cause confidence is based on the specialist investigator's HIGH-confidence hypothesis evaluation, not on independent validation.
2. The formal 5-dimension self-disproof module was not executed -- the above assessment is based on the investigator's contradicting evidence evaluation.
3. The Corrective Action Executor was not run -- no SMART action register was generated.
4. The reason for S002's unit cost increase (30 to 40) is unknown -- requires supplier investigation to determine if temporary or permanent.
5. Whether the cost increase is specific to S002 or part of a broader market trend is unknown.
