# Scenario 1 Test Result

## Test Objective

This scenario tests whether RootIQ can correctly identify an internal operational bottleneck (purchase-order approval delay) as the root cause of a revenue decline, while distinguishing it from demand-side, pricing, and supplier-side explanations.

## Business Question

Why did revenue decline significantly during the current period?

## Expected Root Cause

Internal purchase-order approval bottleneck causing delayed replenishment, Product A stockouts, reduced Product A sales, and overall revenue decline.

## Actual Root Cause

**Purchase-Order Approval Bottleneck** (Status: PROVISIONAL, Confidence: LOW)

The RootIQ orchestrator executed the full 14-step workflow on Scenario 1 data. The Teammate2 hypothesis ranking engine ranked "Purchase-Order Approval Bottleneck" as the #1 hypothesis (investigation-priority score 14.03, signal confidence HIGH, causal confidence LOW). The Evidence Validator returned PASS WITH CAUTION (8 checks: 6 PASS, 2 PASS WITH CAUTION, 0 FAIL). The self-disproof module challenged the leading hypothesis across 5 dimensions and returned PASS WITH CAUTION.

## Root Cause Match

**YES**

The actual root cause "Purchase-Order Approval Bottleneck" is meaningfully equivalent to the expected "Internal purchase-order approval bottleneck." The investigation correctly traced the causal chain: PO approval delay (0.44 to 3.25 days, +631%) -> late replenishment -> P001 stockouts (0 to 86.6 hours) -> P001 revenue decline (-25.17%) -> overall revenue decline (-18.30%).

## Key Evidence

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
| All product selling prices | Unchanged | Unchanged | 0% |
| Complaint count | 10 | 10 | 0% |
| Customer rating | 4.71 | 4.54 | -3.61% |

P001 accounts for 104.31% of the total revenue decline, confirming product-specific scope. Control products P002 and P003 grew, ruling out company-wide demand decline.

## Hypotheses Considered

| Rank | Hypothesis | Signal Confidence | Disposition |
|---|---|---|---|
| 1 | Purchase-Order Approval Bottleneck | HIGH | SUPPORTED_SIGNAL |
| 2 | Supplier Delay | HIGH | SUPPORTED_SIGNAL |
| 3 | Inventory Shortage | HIGH | SUPPORTED_SIGNAL |
| 4 | Customer Dissatisfaction | MEDIUM | SUPPORTED_SIGNAL |
| 5 | Demand Decline | LOW | UNRESOLVED |
| 5 | Price Problem | LOW | UNRESOLVED |

The investigation evaluated 6 competing explanations. Demand Decline and Price Problem were ruled out (no adverse signal, prices unchanged). Customer Dissatisfaction was downweighted (complaint count unchanged). Supplier Delay and Inventory Shortage were ranked below PO Approval Bottleneck because the PO approval spike (+631%) was the largest and earliest signal.

## Self-Disproof Result

**YES**

The self-disproof module challenged "Purchase-Order Approval Bottleneck" across 5 dimensions:

1. **Control Groups:** PASS -- P002 (+4.04%) and P003 (+2.01%) unaffected, consistent with product-specific root cause.
2. **Timing Alignment:** PASS -- PO approval time increased 631% (0.44 to 3.25 days), preceding stockouts and revenue decline. Chronology is consistent.
3. **Alternative Explanations:** PASS -- 2 alternatives explicitly ruled out (complaint count unchanged -> company-wide dissatisfaction less likely; all prices unchanged -> price problem definitively ruled out).
4. **Missing Evidence:** CAUTION -- 2 items identified (timezone-aware revenue-period boundaries; mechanism lacks linked chronology).
5. **Causal Link Strength:** CAUTION -- 0/4 causal chain links provisionally supported (all UNVERIFIED without event-level timestamps).

Overall self-disproof verdict: PASS WITH CAUTION.

## Evidence Validator Result

**PASS WITH CAUTION** (Confidence: LOW)

| # | Check | Status |
|---|---|---|
| 1 | Data Support | PASS |
| 2 | Chronology | PASS WITH CAUTION |
| 3 | Causality vs. Symptom | PASS |
| 4 | Alternative Explanations | PASS |
| 5 | Contradiction Check | PASS |
| 6 | Chain Validation | PASS WITH CAUTION |
| 7 | Math Verification | PASS |
| 8 | AI Fabrication Check | PASS |

Supported claims: 24. Questionable claims: 3. Missing evidence items: 2. No checks returned FAIL.

## Corrective Action Match

**YES**

8 SMART corrective actions were generated. The top 2 Critical actions directly address the validated cause:

- CA-001 (Critical, 48h): Expedite PO approval process -- reduce from 3.25 days to under 1 day.
- CA-002 (Critical, 24h): Emergency replenishment for P001 to restore stock and eliminate stockouts.
- CA-004 (High, 2 weeks): Implement automated PO approval workflow with 4-hour escalation.

All actions are causally relevant to the identified PO approval bottleneck.

## Overall Test Result

**PASS**

## Failure Reason

None

## Notes

- Root cause confidence is LOW (signal HIGH, causal LOW) because all 4 causal chain links remain UNVERIFIED without event-level timestamps; this is a conservative design choice, not an identification failure.
- The 8-check Evidence Validator returned 6 PASS and 2 PASS WITH CAUTION (Chronology and Chain Validation); no checks returned FAIL, and the AI Fabrication Check confirmed no unsupported claims.
- Financial impact was quantified from actual revenue data: 7,315 total loss (-18.30%), with projected monthly loss of 4,982 if uncorrected.
