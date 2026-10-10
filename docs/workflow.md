# RootIQ End-to-End Workflow

## User Journey

RootIQ executes a 14-step workflow from data upload to management-ready report. Each step has a defined input, output, and responsible component.

### Step 1: User Uploads Excel/CSV Data

The SME owner provides an Excel workbook (`.xlsx`) or CSV files containing business data across up to 6 sheets: Sales, Inventory, Purchase_Orders, Suppliers, Customer_Feedback, and Operations. The workbook must include a date column on each sheet for period tagging.

### Step 2: User States One Business Problem

The owner states a single question, such as:
- "Why did revenue drop this month?"
- "Why did our profit margin fall?"
- "Why are customer complaints rising?"

This question becomes the investigation objective. All downstream analysis serves this question.

### Step 3: Orchestrator Interprets the Goal

The RootIQ Orchestrator receives the handoff JSON (containing verified analysis results) and the business problem. It identifies the primary metric, defines the baseline and current periods, and determines which evidence domains are relevant.

### Step 4: Data Analyzer Performs Deterministic Calculations

The SME Business Data Analyzer computes 28+ metrics across 6 business areas, tags records into baseline (28 days) and current (28 days) periods, detects anomalies via 19 rules, and ranks anomalies by composite score. No LLM is used -- every number is from deterministic code.

### Step 5: Evidence Package Is Created

The analysis results are structured into a handoff JSON with standardized sections: overall metrics, product findings, inventory evidence, procurement evidence, supplier evidence, customer evidence, operations evidence, ranked anomalies, and data quality assessment. This package is the single source of truth for all downstream components.

### Step 6: Relevant Specialists Are Selected

The Orchestrator routes evidence to the appropriate specialists based on available data:
- Sales evidence -> Sales Performance Investigator
- Inventory + Procurement evidence -> Inventory & Procurement Investigator (Role 2A)
- Customer + Operations evidence -> Customer & Operations Investigator (Role 2B)

### Step 7: Multiple Hypotheses Are Generated

Each specialist generates 3-4 competing hypotheses within their domain. Each hypothesis includes:
- Supporting evidence (with specific metrics)
- Contradicting evidence (if any)
- Missing evidence (explicitly retained as unknown)
- Confidence level (HIGH / MEDIUM / LOW)

### Step 8: Suspects Are Ranked

The Hypothesis Ranking engine (Role 2C) collects all hypotheses, computes a composite priority score for each (magnitude x relevance x weight), and proposes the highest-ranked hypothesis as the provisional root cause. The ranking is evidence-based, not intuition-based.

### Step 9: Leading Hypothesis Is Challenged

The Self-Disproof module challenges the leading hypothesis across 5 dimensions:
1. **Control groups** -- Are unaffected entities consistent with the hypothesis?
2. **Timing alignment** -- Does the cause precede the effect?
3. **Alternative explanations** -- What else could explain the symptom?
4. **Missing evidence** -- What evidence is unavailable?
5. **Causal link strength** -- Are the causal chain links verified?

### Step 10: Evidence Validator Reviews the Conclusion

The Evidence Validator (Role 2D) runs 8 independent checks:
1. Data Support
2. Chronology
3. Causality vs. Symptom
4. Alternative Explanations
5. Contradiction Check
6. Chain Validation
7. Math Verification
8. AI Fabrication Check

The validator returns PASS, PASS WITH CAUTION, or FAIL.

### Step 11: Failed Validation Causes Revision

If the Evidence Validator returns FAIL, the Orchestrator routes back to the hypothesis ranking stage (Step 8) for revision. The leading hypothesis is demoted, alternatives are re-evaluated, and the cycle repeats until a hypothesis passes validation or the system reports insufficient evidence.

### Step 12: Validated Root Cause Moves to Corrective Action Executor

Once the Evidence Validator returns PASS or PASS WITH CAUTION, the validated root cause is passed to the Corrective Action Executor. The executor generates SMART actions (Specific, Measurable, Achievable, Relevant, Time-bound), each tied to an evidence reference from the validated conclusion.

### Step 13: Final Report and Action Register Are Produced

The Orchestrator generates the final output artifacts:
- An 11-section management report (Markdown)
- A structured case result (JSON)
- A validation report with self-disproof results (JSON)
- A SMART action register (CSV)

---

## Example Scenario

Using Scenario 1 -- "Why did revenue drop this month?"

### Evidence Chain

```
Revenue declined 18.30% (39,975 -> 32,660)
  |
  v
Product A (P001) revenue declined 25.17% (30,310 -> 22,680)
  |-- P001 accounts for 104.31% of total decline
  |-- P002 grew +4.04%, P003 grew +2.01% (control products unaffected)
  |
  v
P001 stockout hours surged 0 -> 86.6 hours
  |-- P001 availability dropped 100% -> 87.11%
  |-- P001 closing stock declined 60.48%
  |
  v
Replenishment was delayed
  |-- S001 supplier lead time increased 3.33 -> 4.0 days (+66.67%)
  |-- Procurement fulfilment time increased 3.78 -> 7.25 days (+91.91%)
  |
  v
Purchase-order approval was delayed
  |-- PO approval time spiked 0.44 -> 3.25 days (+631.25%)
  |-- This is the #1 ranked anomaly by composite score
  |
  v
VALIDATED CAUSE: Purchase-Order Approval Bottleneck
  (Confidence: LOW | Status: PROVISIONAL)
  (Self-Disproof: PASS WITH CAUTION | Validator: PASS WITH CAUTION)
```

### Key Supporting Evidence

- All selling prices unchanged (rules out price problem)
- Complaint count unchanged at 10 (rules out company-wide dissatisfaction)
- P002 and P003 revenue grew (confirms product-specific scope)
- PO approval spike is the earliest and largest signal in the chronology

### Corrective Actions Generated

| Priority | Action | Deadline |
|---|---|---|
| Critical | Expedite PO approval process (3.25 days -> < 1 day) | 48 hours |
| Critical | Emergency replenishment for P001 | 24 hours |
| High | Contact Supplier S001 on lead time increase | 72 hours |
| High | Implement automated PO approval with 4-hour escalation | 2 weeks |

---

## Error Handling

### Data-Quality Failure

If the Data Analyzer detects critical data quality issues (missing required columns, unparseable dates, non-numeric values in required fields), it returns a data quality warning in the output JSON. The Orchestrator checks the data quality status before proceeding. If status is FAIL, the investigation halts and the user is informed of the specific data issue.

### Missing Evidence

When the self-disproof module identifies missing evidence (e.g., foot traffic data not available, timezone-aware timestamps not present), it explicitly retains these gaps as "unknown" rather than fabricating values. The Evidence Validator's Missing Evidence check records the count. The final report includes these gaps transparently.

### Validator FAIL

If the Evidence Validator returns FAIL, the Orchestrator routes back to hypothesis ranking. The leading hypothesis is demoted, the next-ranked hypothesis is evaluated, and the self-disproof + validation cycle repeats. If all hypotheses fail validation, the system reports "No confirmed root cause" rather than forcing a conclusion.

### Component Failure

If the Teammate2 engine fails to load or crashes during execution, the Orchestrator catches the error, logs it in the investigation trace, and continues in partial mode (producing a report with the available evidence but without formal validation). The report clearly states which stages were not completed.

### No Confirmed Root Cause

If no hypothesis passes validation, the Orchestrator produces a report stating that no root cause could be confirmed from the available evidence. The report includes the ranked hypotheses, the validation failures, and the missing evidence items, allowing the user to make a decision about additional data collection.

---

## Output Artifacts

The RootIQ workflow produces 7 output artifacts in the output directory:

### Primary Deliverables

| File | Format | Content |
|---|---|---|
| `rootiq_final_report.md` | Markdown | 11-section management-ready report: executive summary, business problem, investigation approach, evidence summary, root cause analysis, causal chain, financial impact, validation results, self-disproof analysis, corrective actions, action register summary. |
| `rootiq_case_result.json` | JSON | Structured case summary: case ID, timestamp, business problem, proposed root cause, confidence, status, self-disproof verdict, evidence validation status, financial impact, action counts, components used. |
| `rootiq_validation_report.json` | JSON | Full validation detail: 8-check validator results with per-check status, supported/questionable/missing claim counts, self-disproof 5-dimension challenge results with dispositions, mapping trace. |
| `rootiq_action_register.csv` | CSV | SMART action register: action ID, type (Immediate/Preventive/Monitoring), priority (Critical/High/Medium), action description, owner, deadline, success metric, current value, target value, evidence reference. |

### Supporting Artifacts

| File | Format | Content |
|---|---|---|
| `rootiq_investigation_trace.json` | JSON | Full audit trace of all 14 steps, including inputs, outputs, and timestamps for each step. Enables post-hoc review of the investigation process. |
| `rootiq_teammate2_payload.json` | JSON | The mapped input payload sent to the Teammate2 engine (flat metrics + structured sections). Enables debugging and reproducibility. |
| `rootiq_teammate2_raw_result.json` | JSON | Raw output from the Teammate2 engine, including all hypothesis rankings, causal chain links, and validation checks. Full evidence for the final report. |

### Demo Command

```bash
python rootiq_orchestrator.py --handoff scenario_1_handoff.json --output-dir ./rootiq_output
```
