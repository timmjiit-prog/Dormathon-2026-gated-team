# RootIQ Investigation Report

**Case ID:** scenario_1
**Investigation Date:** 2026-10-10
**Engine:** RootIQ Autonomous Root Cause Investigator v1.0.0

---

## Executive Summary

Overall revenue declined 18.30% (39,975 to 32,660) comparing the current period against the baseline period. The validated root cause is a Purchase-Order Approval Bottleneck -- PO approval time spiked 631% (0.44 to 3.25 days), causing delayed replenishment, Product A stockouts, and product-specific revenue decline. Confidence is LOW (signal HIGH, causal LOW) because causal chain links remain unverified without event-level timestamps. The highest-priority action is to expedite the PO approval process from 3.25 days to under 1 day within 48 hours.

## Business Problem

Why did revenue decline significantly during the current period?

## Investigation Period

**Baseline:** 2026-08-03 to 2026-08-30 (28 days)
**Current:** 2026-08-31 to 2026-09-27 (28 days)

## Key Metrics

| Metric | Baseline | Current | Change |
|---|---|---|---|
| Overall revenue | 39,975 | 32,660 | -18.30% |
| P001 (Product A) revenue | 30,310 | 22,680 | -25.17% |
| P001 stockout hours | 0 | 86.6 | base_zero -> spike |
| P001 availability | 100% | 87.11% | -12.89pp |
| PO approval time | 0.44 days | 3.25 days | +631.25% |
| S001 supplier lead time | 3.33 days | 4.0 days | +66.67% |
| Procurement fulfilment time | 3.78 days | 7.25 days | +91.91% |
| P002 revenue (control) | 5,940 | 6,180 | +4.04% |
| P003 revenue (control) | 3,725 | 3,800 | +2.01% |
| All selling prices | Unchanged | Unchanged | 0% |
| Complaint count | 10 | 10 | 0% |

## Ranked Hypotheses

| Rank | Hypothesis | Confidence | Supporting Evidence | Contradicting Evidence |
|---|---|---|---|---|
| 1 | Purchase-Order Approval Bottleneck | HIGH | PO approval +631% (#1 anomaly); P001 stockouts 0->86.6h; P001 revenue -25.17% (104.31% of decline); fulfilment +91.91% | None identified |
| 2 | Supplier Delay | HIGH | S001 lead time +66.67% (3->5d); S001 OTD derived 100%->0% | S001 OTD reported 88% (no period split); supplier delay alone does not explain P001-specific scope |
| 3 | Inventory Shortage | HIGH | P001 closing stock -60.48%; P001 availability 100%->87.11% | Inventory shortage is a symptom, not a cause; stockouts are downstream of replenishment delay |
| 4 | Customer Dissatisfaction | MEDIUM | Rating -3.61%; cancellations +13.04% | Complaint count unchanged (10->10); revenue decline is product-specific, not company-wide |
| 5 | Demand Decline | LOW | -- | P002 +4.04% and P003 +2.01% grew while P001 declined; foot traffic data unavailable but control products suggest product-specific issue |
| 6 | Price Problem | LOW | -- | All product prices unchanged (0% change); definitively ruled out |

## Root Cause Chain

```
Observed Problem: Revenue declined 18.30% (39,975 -> 32,660)
      ↓
Contributing Factor: P001 revenue declined 25.17% (104.31% of total decline)
      ↓
Intermediate Cause: P001 stockouts surged 0 -> 86.6 hours (availability 100% -> 87.11%)
      ↓
Underlying Cause: Replenishment delayed (S001 lead 3.33->4.0d, fulfilment 3.78->7.25d)
      ↓
Validated Root Cause: PO approval time spiked 631% (0.44 -> 3.25 days)
      [Status: PROVISIONAL | Confidence: LOW]
```

**Chain Confidence:** LOW -- All 4 causal links are UNVERIFIED (require event-level timestamps to upgrade).

## Supporting Evidence

1. PO approval time increased 631.25% (0.44 to 3.25 days) -- #1 ranked anomaly by composite score
2. P001 stockout hours surged from 0 to 86.6 hours -- #6 ranked anomaly
3. P001 revenue declined 25.17%, accounting for 104.31% of total revenue decline
4. P001 closing stock declined 60.48% from baseline levels
5. S001 supplier lead time increased 66.67% (3.33 to 4.0 days)
6. Procurement fulfilment time increased 91.91% (3.78 to 7.25 days)
7. P002 and P003 revenue grew (+4.04% and +2.01%), confirming product-specific scope
8. All selling prices unchanged across all products (0% change)

## Contradicting Evidence

1. Complaint count was unchanged (10 -> 10), ruling out company-wide customer dissatisfaction
2. All product prices were unchanged, definitively ruling out a pricing problem
3. P002 and P003 grew while P001 declined, ruling out a broad demand decline
4. Foot traffic / demand data was not available -- demand decline cannot be fully ruled out, but control products strongly suggest a product-specific issue

## Self-Disproof Result

- **Leading hypothesis tested:** Purchase-Order Approval Bottleneck
- **Survived challenge:** YES (PASS WITH CAUTION)
- **Control groups:** PASS -- P002 (+4.04%) and P003 (+2.01%) unaffected, consistent with product-specific cause
- **Timing alignment:** PASS -- PO approval spike preceded stockouts and revenue decline
- **Alternative explanations:** PASS -- 2 alternatives ruled out (customer dissatisfaction, price problem)
- **Missing evidence:** CAUTION -- 2 items (timezone-aware timestamps, mechanism chronology)
- **Causal link strength:** CAUTION -- 0/4 links provisionally supported (all UNVERIFIED)
- **Stronger alternative found:** NO

## Evidence Validation

- **Validator status:** PASS WITH CAUTION
- **Confidence:** LOW
- **Supported claims:** 24
- **Questionable claims:** 3
- **Missing evidence items:** 2
- **Per-check results:** Data Support PASS | Chronology CAUTION | Causality PASS | Alternatives PASS | Contradiction PASS | Chain Validation CAUTION | Math PASS | AI Fabrication PASS
- **Required corrections:**
  1. Provide or explicitly retain as unknown: Timezone-aware revenue-period boundaries and matching outcome timestamp
  2. Provide or explicitly retain as unknown: Submitted mechanism lacks a relevant metric or valid linked chronology

## Business Impact

| Metric | Value | Type |
|---|---|---|
| Total revenue loss | 7,315 | EXACT |
| Revenue decline percentage | -18.30% | EXACT |
| P001 revenue loss | 7,630 | EXACT |
| P001 contribution to decline | 104.31% | EXACT |
| Projected monthly loss if uncorrected | 4,982 | ESTIMATE |

## Immediate Corrective Action

**CA-001 (Critical, 48 hours):** Expedite purchase order approval process -- reduce approval time from 3.25 days to under 1 day. Owner: Purchasing Manager. Success metric: PO approval time < 1 day for P001 orders.

## Preventive Action

**CA-004 (High, 2 weeks):** Implement automated PO approval workflow with escalation after 4 hours if primary approver unavailable. Owner: Operations Manager. Success metric: Zero PO approvals exceeding 1 day; escalation triggered within 4 hours.

## Monitoring KPI

| KPI | Normal Range | Warning Threshold | Critical Threshold |
|---|---|---|---|
| PO approval time | < 1 day | > 1 day | > 2 days |
| P001 stockout hours | 0 hours | > 0 hours | > 24 hours |
| P001 closing stock | > 120 units | < 120 units | < 60 units |
| Supplier lead time (S001) | <= 3 days | > 3 days | > 4 days |

## Action Register

| ID | Type | Priority | Action | Owner | Deadline |
|---|---|---|---|---|---|
| CA-001 | Immediate | Critical | Expedite PO approval (3.25d -> <1d) | Purchasing Manager | 48 hours |
| CA-002 | Immediate | Critical | Emergency replenishment for P001 | Inventory Manager | 24 hours |
| CA-003 | Immediate | High | Contact S001 on lead time increase | Purchasing Manager | 72 hours |
| CA-004 | Preventive | High | Automated PO approval with 4h escalation | Operations Manager | 2 weeks |
| CA-005 | Preventive | Medium | Min stock buffer P001 at 120 units | Inventory Manager | 1 week |
| CA-006 | Preventive | Medium | Diversify supplier base for P001 | Purchasing Manager | 4 weeks |
| CA-007 | Monitoring | High | Daily monitoring dashboard | Operations Manager | 1 week |
| CA-008 | Monitoring | Medium | Weekly supplier performance review | Purchasing Manager | 2 weeks |

**Total:** 8 actions (2 Critical, 3 High, 3 Medium)

## Limitations / Missing Evidence

1. Causal chain links are UNVERIFIED -- event-level timestamps are required to upgrade from PROVISIONAL to SUPPORTED. The period-comparison approach cannot establish causality at the event level.
2. Foot traffic / demand data was not available -- demand decline cannot be fully ruled out, though control products (P002, P003) strongly suggest a product-specific issue.
3. Timezone-aware revenue-period boundaries were not available -- the validator flagged this as a missing evidence item.
4. Root cause confidence is LOW (signal HIGH, causal LOW) by conservative design -- the system does not declare causal certainty without event-linked evidence.
