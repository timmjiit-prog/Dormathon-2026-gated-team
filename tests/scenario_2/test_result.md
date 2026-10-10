# Scenario 2 Test Result

## Test Objective

This scenario tests whether RootIQ can identify a cost/margin problem (supplier-driven unit-cost inflation causing margin compression) instead of incorrectly blaming sales, pricing, inventory, or procurement factors. The key challenge is that revenue remains broadly stable, so the system must look beyond top-line metrics to find the profit erosion.

## Business Question

Why did gross profit and gross margin fall even though revenue remained broadly stable?

## Expected Root Cause

Material increase in Product B supplier/unit cost causing higher COGS and margin compression while selling prices remained broadly unchanged.

## Actual Root Cause

**Supplier cost increase (S002 driving P002 unit cost inflation)** (Confidence: HIGH)

The SME Business Data Analyzer computed 29 metrics across 6 domains and detected 8 anomalies (all CRITICAL). The Sales Investigator evaluated 4 competing hypotheses and ranked "Supplier cost increase (S002 driving P002 unit cost inflation)" as the #1 hypothesis with HIGH confidence. The primary finding identified P002 as the sole driver: P002 unit cost increased 33.33% (30 to 40), matching S002's supplier unit cost increase exactly, with zero selling price change.

Note: The full 14-step orchestrator (formal self-disproof module, 8-check evidence validator, and corrective action executor) was executed end-to-end only for Scenario 1. For Scenario 2, the analysis and specialist investigator stages were completed; downstream orchestrator stages were not executed.

## Root Cause Match

**YES**

The actual root cause "Supplier cost increase (S002 driving P002 unit cost inflation)" matches the expected "Material increase in Product B supplier/unit cost causing higher COGS and margin compression." The evidence chain is: S002 unit cost +33.33% (30 to 40) -> P002 unit cost +33.33% (30 to 40) -> P002 COGS +32.08% (9,600 to 12,680) -> P002 gross profit -33.96% (9,600 to 6,340) -> overall gross profit -16.93% (20,120 to 16,713).

## Key Evidence

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
| S001 unit cost (control) | 20 | 20.5 | +2.5% |
| S003 unit cost (control) | 15 | 15.2 | +1.33% |
| P001 unit cost (control) | 20 | 20.5 | +2.5% |
| P003 unit cost (control) | 15 | 15.2 | +1.33% |
| All selling prices | Unchanged | Unchanged | 0% |
| Inventory stockout hours (all) | 0 | 0 | 0 |
| Inventory availability (all) | 100% | 100% | 0pp |
| PO approval time | 0.56 days | 0.33 days | -40% (improved) |
| Supplier lead time | 3.33 days | 3.33 days | 0% |
| Late PO orders | 0 | 0 | 0 |
| Complaint rate | 7.14% | 21.43% | +200% |
| Customer rating | 4.57 | 4.46 | -2.34% |

P002 accounts for 128.57% of the total gross profit decline, confirming product-specific scope. Control products P001 and P003 have minimal cost changes (+2.5% and +1.33% respectively).

## Hypotheses Considered

| Rank | Hypothesis | Confidence | Disposition |
|---|---|---|---|
| 1 | Supplier cost increase (S002 driving P002 unit cost inflation) | HIGH | Supported |
| 2 | Product-specific cost issue (P002 only, not company-wide) | HIGH | Supported |
| 3 | Revenue or price decline causing profit drop | LOW | Contradicted |
| 4 | Inventory shortage or stockout impact | LOW | Contradicted |

The investigator evaluated 4 competing explanations. Hypothesis 3 was contradicted (all prices unchanged, 0.37% revenue change cannot explain 16.93% profit decline). Hypothesis 4 was contradicted (0 stockout hours, 100% availability, increasing closing stock across all products).

## Self-Disproof Result

**YES**

The specialist investigator actively challenged the leading hypothesis by evaluating contradicting evidence and alternative explanations:

- **Control products:** P001 unit cost +2.5% and P003 unit cost +1.33% (minimal) vs P002 +33.33% (severe), confirming product-specific scope.
- **Alternative: Revenue/price decline:** Contradicted -- all selling prices unchanged (P001 45, P002 60, P003 35); 0.37% revenue change cannot explain 16.93% profit decline; P003 revenue grew +2.62%.
- **Alternative: Inventory shortage:** Contradicted -- 0 stockout hours, 100% availability, closing stock increased for all products (P001 +12.9%, P002 +27.02%, P003 +33.37%).
- **Missing evidence:** Reason for S002 unit cost increase requires supplier investigation; whether temporary or permanent is unknown.

Note: The formal 5-dimension self-disproof module was not executed for this scenario. The above assessment is based on the specialist investigator's hypothesis evaluation, which includes supporting, contradicting, and missing evidence.

## Evidence Validator Result

**Not recorded**

The formal 8-check Evidence Validator (Teammate2 Role 2D) was not executed for this scenario. Validation was not performed at the orchestrator level.

## Corrective Action Match

**Not recorded**

The Corrective Action Executor was not run for this scenario. No SMART action register was generated.

## Overall Test Result

**PASS**

Root cause correctly identified with HIGH confidence. The leading hypothesis matches the expected cause, supported by strong product-specific and supplier-specific evidence with control product comparisons. The investigation correctly rejected inventory and pricing explanations.

## Failure Reason

None

## Notes

- The analysis and specialist investigator stages were completed; the formal orchestrator-level validation (self-disproof, evidence validator, corrective actions) was not executed for this scenario.
- The root cause identification is well-supported: S002 unit cost +33.33% exactly matches P002 unit cost +33.33%, with all selling prices unchanged and inventory healthy.
- P002 accounts for 128.57% of the total gross profit decline, meaning other products partially offset the decline, confirming product-specific scope.
