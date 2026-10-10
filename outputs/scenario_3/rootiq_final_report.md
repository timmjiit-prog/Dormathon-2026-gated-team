# RootIQ Investigation Report

**Case ID:** scenario_3
**Investigation Date:** 2026-10-10
**Engine:** RootIQ Autonomous Root Cause Investigator v1.0.0

---

## Executive Summary

Customer complaints rose 233.33% (12 to 40) and late deliveries surged 108.97% (145 to 303) while revenue remained stable (+0.9%, 26,650 to 26,890). The validated root cause is an Evening Shift Staffing Shortfall -- Evening staff halved (4 to 2, -50%), causing Evening late orders to surge from 0 to 148 and Evening fulfilment time to increase 66.18% (2.29h to 3.8h). Confidence is HIGH. The highest-priority action is to investigate the Evening staffing reduction and restore staffing to required levels within 48 hours.

## Business Problem

Why did customer complaints and late deliveries rise sharply?

## Investigation Period

**Baseline:** 2026-08-03 to 2026-08-30 (28 days)
**Current:** 2026-08-31 to 2026-09-27 (28 days)

## Key Metrics

| Metric | Baseline | Current | Change |
|---|---|---|---|
| Complaint count | 12 | 40 | +233.33% |
| Complaint rate | 15.19% | 50.63% | +35.44pp |
| Delivery-delay complaints | 4 | 31 | +675% |
| Delivery-delay complaint share | 33.33% | 77.5% | +44.17pp |
| Avg actual staff (ALL) | 3.5 | 2.5 | -28.57% |
| Required staff (ALL) | 3.5 | 3.5 | 0% (unchanged) |
| Evening actual staff | 4 | 2 | -50.00% |
| Day actual staff | 3 | 3 | 0% (stable) |
| Late orders (ALL) | 145 | 303 | +108.97% |
| Evening late orders | 0 | 148 | base_zero -> spike |
| Day late orders | 145 | 155 | +6.90% (stable) |
| Fulfilment time (ALL) | 2.81h | 3.60h | +28.11% |
| Evening fulfilment time | 2.29h | 3.80h | +66.18% |
| Day fulfilment time | 3.34h | 3.41h | +2.04% (stable) |
| Total capacity orders | 3,332 | 2,380 | -28.57% |
| Fulfilment rate | 93.29% | 86.23% | -7.06pp |
| Customer rating | 4.46 | 3.87 | -13.07% |
| Revenue | 26,650 | 26,890 | +0.90% (stable) |
| All selling prices | Unchanged | Unchanged | 0% |
| Inventory stockout hours | 0 | 0 | 0 |
| Supplier lead time | 3.33 days | 3.33 days | 0% |
| All supplier unit costs | Unchanged | Unchanged | 0% |
| All supplier OTD rates | 100% | 100% | 0pp |

## Ranked Hypotheses

| Rank | Hypothesis | Confidence | Supporting Evidence | Contradicting Evidence |
|---|---|---|---|---|
| 1 | Evening shift staffing shortfall driving late deliveries and complaints | HIGH | Evening staff -50% (4->2); Evening late orders 0->148; Evening fulfilment +66.18%; 148 of 303 late orders from Evening; staffing gap 1.0 FTE; capacity -28.57%; Day shift stable | Revenue stable (+0.9%); Day shift normal |
| 2 | Overall operational capacity reduction causing service degradation | HIGH | Staff -28.57%; capacity -28.57%; fulfilled -6.96%; fulfilment rate -7.06pp; fulfilment time +28.11%; utilization 76.74%->99.96% | Orders received stable (+0.66%); revenue stable (+0.9%) |
| 3 | Delivery delays driving the complaint surge | HIGH | Delivery-delay complaints 4->31 (share 33.33%->77.5%); late orders +108.97%; fulfilment time +28.11%; complaint rate +233.33%; rating -13.07% | Packaging complaints declined (4->3); Product Quality complaints modest (4->6) |
| 4 | Supply chain disruption causing late deliveries | LOW | -- | 7 items: all supplier lead times/costs/OTD unchanged; procurement lead time unchanged; 0 late PO orders; inventory healthy; procurement fulfilment only +10% vs ops +28.11% |

## Root Cause Chain

```
Observed Problem: Complaints rose 233.33% (12 -> 40) and late orders rose 108.97% (145 -> 303)
      ↓
Contributing Factor: Delivery-delay complaints surged 4 -> 31 (share 33.33% -> 77.5%)
      ↓
Intermediate Cause: Late orders increased 108.97% with 148 of 303 from Evening shift alone
      ↓
Underlying Cause: Evening fulfilment time increased 66.18% (2.29h -> 3.8h) while Day was stable (+2.04%)
      ↓
Validated Root Cause: Evening shift staff halved (4 -> 2, -50%) creating 1.0 FTE staffing gap
      [Confidence: HIGH]
```

## Supporting Evidence

1. Evening actual staff decreased 50.00% (4 to 2) while Day staff was unchanged (3 to 3)
2. Evening late orders surged from 0 to 148 (base_zero) -- 148 of 303 total late orders
3. Evening fulfilment time increased 66.18% (2.29h to 3.8h, +1.51h)
4. Day shift late orders only increased 6.9% (145 to 155) vs Evening's 0 to 148
5. Day shift fulfilment time only increased 2.04% (3.34h to 3.41h) -- Day is stable
6. Staffing gap of 1.0 FTE appeared in current period (required 3.5, actual 2.5)
7. Total capacity orders fell 28.57% (3,332 to 2,380), matching the staff reduction rate exactly
8. Capacity utilization rose from 76.74% to 99.96% (+23.22pp) -- system near saturation
9. Complaint rate rose 233.33% (15.19% to 50.63%)
10. Delivery-delay complaint share rose from 33.33% to 77.5% (+44.17pp)

## Contradicting Evidence

1. All supplier lead times were unchanged (S001 3.0d, S002 3.0d, S003 4.0d, 0% change)
2. All supplier unit costs were unchanged (S001 24, S002 18, S003 14, 0% change)
3. All supplier OTD derived rates were at 100% (0pp change)
4. Procurement supplier lead time was unchanged at 3.33 days
5. Procurement late PO orders were at 0 in both periods
6. Inventory was healthy: 0 stockout hours, 100% availability, increasing closing stock for all products
7. Procurement fulfilment time only increased 10% (3.33d to 3.67d), minor compared to operations +28.11%
8. Orders received were stable (+0.66%, 2,741 to 2,759) -- demand did not increase
9. Revenue was stable (+0.9%, 26,650 to 26,890) -- no revenue impact from service degradation
10. Packaging complaints declined (4 to 3, share 33.33% to 7.5%, -25.83pp)

## Self-Disproof Result

- **Leading hypothesis tested:** Evening shift staffing shortfall driving late deliveries and complaints
- **Survived challenge:** YES
- **Control groups:** Day shift staff unchanged (3 to 3), Day late orders +6.9% (145 to 155), Day fulfilment +2.04% (3.34h to 3.41h) -- Day stable, isolating problem to Evening
- **Alternative: Supply chain disruption:** Contradicted by 7 items (all supplier metrics unchanged, procurement normal, inventory healthy)
- **Alternative: Demand surge:** Contradicted -- orders received stable (+0.66%), revenue stable (+0.9%)
- **Missing evidence:** Reason for Evening staff reduction (resignation, schedule change, hiring failure) requires HR investigation; whether planned or unplanned is unknown; exact timing within period not available at daily granularity
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
| Complaint increase | +28 (12 to 40) | EXACT |
| Complaint rate increase | +35.44pp (15.19% to 50.63%) | EXACT |
| Late order increase | +158 (145 to 303) | EXACT |
| Fulfilment rate decline | -7.06pp (93.29% to 86.23%) | EXACT |
| Evening staff reduction | -2 FTE (4 to 2) | EXACT |
| Capacity reduction | -952 orders (3,332 to 2,380) | EXACT |
| Customer rating decline | -0.59 (4.46 to 3.87) | EXACT |

## Immediate Corrective Action

Investigate the Evening shift staff reduction (4 to 2, -50%) -- determine whether it was planned or unplanned (resignation, schedule change, hiring failure), and restore Evening staffing to required levels (4 FTE) immediately. Owner: Shift Supervisor / Operations Manager. Deadline: 48 hours.

Note: This action is derived from the investigator's recommended next investigation, not from a formal Corrective Action Executor run.

## Preventive Action

Implement staffing level monitoring with automated alerts when actual staff falls below required staff for any shift. Establish a backup staffing protocol for Evening shifts to prevent single-point-of-failure staffing gaps.

Note: Not generated by the formal Corrective Action Executor.

## Monitoring KPI

| KPI | Normal Range | Warning Threshold | Critical Threshold |
|---|---|---|---|
| Evening shift actual staff | >= required staff | < required staff | < 50% of required |
| Late orders (Evening) | <= 10 | > 10 | > 50 |
| Fulfilment time (Evening) | <= 2.5h | > 3.0h | > 3.5h |
| Overall fulfilment rate | >= 93% | < 90% | < 86% |
| Complaint rate | <= 15% | > 20% | > 40% |

Note: Monitoring KPIs are derived from the verified metrics, not from a formal Corrective Action Executor run.

## Action Register

Not recorded. The Corrective Action Executor was not run for this scenario. The investigator recommended next investigation domain: Operations/HR.

## Limitations / Missing Evidence

1. The formal 8-check Evidence Validator was not executed -- root cause confidence is based on the specialist investigator's HIGH-confidence hypothesis evaluation, not on independent validation.
2. The formal 5-dimension self-disproof module was not executed -- the above assessment is based on the investigator's contradicting evidence evaluation.
3. The Corrective Action Executor was not run -- no SMART action register was generated.
4. The reason for the Evening staff reduction (4 to 2) is unknown -- requires HR investigation to determine if it was a resignation, schedule change, or hiring failure.
5. Whether the staff reduction was planned or unplanned is unknown.
6. The exact timing of the staff reduction within the current period is not available at daily granularity.
