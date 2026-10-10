# Scenario 3 Test Result

## Test Objective

This scenario tests whether RootIQ can identify an operations/staffing cause (Evening-shift capacity bottleneck) while rejecting inventory, supplier, and procurement explanations. The key challenge is distinguishing an internal staffing problem from supply chain disruption when both could theoretically cause late deliveries.

## Business Question

Why did customer complaints and late deliveries rise sharply?

## Expected Root Cause

Evening-shift staffing/capacity bottleneck causing fulfilment delays, late orders, and increased delivery-delay complaints.

## Actual Root Cause

**Evening shift staffing shortfall driving late deliveries and complaints** (Confidence: HIGH)

The SME Business Data Analyzer computed metrics across 6 domains (including Operations) and detected 6 anomalies (4 CRITICAL + 2 HIGH). The Customer & Operations Investigator evaluated 4 competing hypotheses and ranked "Evening shift staffing shortfall driving late deliveries and complaints" as the #1 hypothesis with HIGH confidence. The primary finding identified the Evening shift as the core problem: Evening staff halved (4 to 2, -50%), Evening late orders surged from 0 to 148, and Evening fulfilment time rose 66.18% (2.29h to 3.8h), while the Day shift remained stable.

Note: The full 14-step orchestrator (formal self-disproof module, 8-check evidence validator, and corrective action executor) was executed end-to-end only for Scenario 1. For Scenario 3, the analysis and specialist investigator stages were completed; downstream orchestrator stages were not executed.

## Root Cause Match

**YES**

The actual root cause "Evening shift staffing shortfall driving late deliveries and complaints" matches the expected "Evening-shift staffing/capacity bottleneck causing fulfilment delays, late orders, and increased delivery-delay complaints." The evidence chain is: Evening staff -50% (4 to 2) -> Evening late orders 0 to 148 -> overall late orders +108.97% (145 to 303) -> delivery-delay complaints 4 to 31 (share 33.33% to 77.5%) -> complaint rate +233.33% (15.19% to 50.63%).

## Key Evidence

| Metric | Baseline | Current | Change |
|---|---|---|---|
| Complaint count | 12 | 40 | +233.33% |
| Complaint rate | 15.19% | 50.63% | +35.44pp |
| Delivery-delay complaints | 4 | 31 | +675% |
| Delivery-delay complaint share | 33.33% | 77.5% | +44.17pp |
| Avg actual staff (ALL) | 3.5 | 2.5 | -28.57% |
| Required staff (ALL) | 3.5 | 3.5 | 0% (unchanged) |
| Staffing gap | 0 | 1.0 FTE | base_zero -> gap |
| Evening actual staff | 4 | 2 | -50.00% |
| Day actual staff | 3 | 3 | 0% (stable) |
| Late orders (ALL) | 145 | 303 | +108.97% |
| Evening late orders | 0 | 148 | base_zero -> spike |
| Day late orders | 145 | 155 | +6.90% (stable) |
| Fulfilment time (ALL) | 2.81h | 3.60h | +28.11% |
| Evening fulfilment time | 2.29h | 3.80h | +66.18% |
| Day fulfilment time | 3.34h | 3.41h | +2.04% (stable) |
| Total capacity orders | 3,332 | 2,380 | -28.57% |
| Orders fulfilled | 2,557 | 2,379 | -6.96% |
| Fulfilment rate | 93.29% | 86.23% | -7.06pp |
| Capacity utilization | 76.74% | 99.96% | +23.22pp |
| Customer rating | 4.46 | 3.87 | -13.07% |
| Cancellation rate | 1.27% | 2.53% | +100% |
| Revenue | 26,650 | 26,890 | +0.90% (stable) |
| All selling prices | Unchanged | Unchanged | 0% |
| Inventory stockout hours (all) | 0 | 0 | 0 |
| Inventory availability (all) | 100% | 100% | 0pp |
| PO approval time | 0 days | 0.33 days | base_zero |
| Supplier lead time | 3.33 days | 3.33 days | 0% |
| Late PO orders | 0 | 0 | 0 |
| All supplier lead times | Unchanged | Unchanged | 0% |
| All supplier unit costs | Unchanged | Unchanged | 0% |
| All supplier OTD rates | 100% | 100% | 0pp |

The Day shift remained stable across all metrics, isolating the problem to the Evening shift. Inventory, procurement, and supplier domains show no anomalies, ruling out supply chain disruption.

## Hypotheses Considered

| Rank | Hypothesis | Confidence | Disposition |
|---|---|---|---|
| 1 | Evening shift staffing shortfall driving late deliveries and complaints | HIGH | Supported |
| 2 | Overall operational capacity reduction causing service degradation | HIGH | Supported |
| 3 | Delivery delays driving the complaint surge | HIGH | Supported |
| 4 | Supply chain disruption causing late deliveries | LOW | Contradicted |

The investigator evaluated 4 competing explanations. Hypothesis 4 (supply chain disruption) was contradicted by 7 items: all supplier lead times/costs/OTD unchanged, procurement normal, inventory healthy.

## Self-Disproof Result

**YES**

The specialist investigator actively challenged the leading hypothesis by evaluating contradicting evidence and alternative explanations:

- **Control groups:** Day shift staff unchanged (3 to 3), Day late orders +6.9% (145 to 155), Day fulfilment +2.04% (3.34h to 3.41h) -- Day shift stable, isolating problem to Evening.
- **Alternative: Supply chain disruption:** Contradicted by 7 items (all supplier lead times unchanged, all supplier unit costs unchanged, all OTD rates at 100%, procurement lead time unchanged at 3.33d, 0 late PO orders, inventory healthy with 0 stockout/100% availability/increasing stock, procurement fulfilment only +10% vs ops +28.11%).
- **Alternative: Demand surge:** Contradicted -- orders received stable (+0.66%, 2,741 to 2,759), revenue stable (+0.9%).
- **Missing evidence:** Reason for Evening staff reduction (resignation, schedule change, hiring failure) requires HR investigation; whether planned or unplanned is unknown; exact timing within period not available at daily granularity.

Note: The formal 5-dimension self-disproof module was not executed for this scenario. The above assessment is based on the specialist investigator's hypothesis evaluation, which includes supporting, contradicting, and missing evidence.

## Evidence Validator Result

**Not recorded**

The formal 8-check Evidence Validator (Teammate2 Role 2D) was not executed for this scenario. Validation was not performed at the orchestrator level.

## Corrective Action Match

**Not recorded**

The Corrective Action Executor was not run for this scenario. No SMART action register was generated.

## Overall Test Result

**PASS**

Root cause correctly identified with HIGH confidence. The leading hypothesis matches the expected cause, supported by strong shift-specific evidence (Evening vs Day comparison) with supply chain, inventory, and procurement domains explicitly ruled out.

## Failure Reason

None

## Notes

- The analysis and specialist investigator stages were completed; the formal orchestrator-level validation (self-disproof, evidence validator, corrective actions) was not executed for this scenario.
- The root cause identification is well-supported: Evening staff -50% (4 to 2) with Day staff unchanged, Evening late orders 0 to 148, and all supply chain metrics stable.
- The investigation correctly rejected supply chain disruption (hypothesis 4, LOW confidence) using 7 contradicting evidence items across supplier, procurement, and inventory domains.
