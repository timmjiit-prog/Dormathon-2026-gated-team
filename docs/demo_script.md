# RootIQ 3-Minute Demo Script

## 0:00-0:25 -- Problem

SMEs often know **what went wrong** but not **why**.

Revenue dropped 18%. Complaints tripled. Profit margin collapsed. A dashboard shows the numbers. But the owner still has to figure out: Was it a supplier problem? A staffing issue? A pricing mistake? An internal process bottleneck?

Most SMEs don't have a dedicated analyst. The owner spends hours -- sometimes days -- pulling spreadsheets, comparing periods, and guessing at causes. By the time they find the answer, the damage has compounded.

RootIQ changes this. It takes the same data and performs the investigation automatically.

---

## 0:25-0:45 -- Solution

**RootIQ is an autonomous AI investigator for SMEs.** Give it your business data and one question -- "Why did revenue drop?" -- and it does the rest:

- Computes every metric deterministically (no AI guessing)
- Generates multiple competing hypotheses
- Ranks them by evidence
- **Actively tries to disprove its own leading hypothesis** before making a claim
- Validates the conclusion through an independent 8-check validator
- Turns the validated cause into SMART corrective actions

**Key line:**

> "RootIQ does not trust its first plausible answer. It generates competing suspects and actively tries to disprove its own leading hypothesis before making a claim."

---

## 0:45-2:10 -- Live Demo

### Setup

Open the WorkBuddy AI workspace with the RootIQ project loaded. Have the Scenario 1 workbook (`RootIQ_SME_Dataset_Scenario1.xlsx`) ready.

### Demo Prompt

Type this exact prompt into the WorkBuddy chat:

```
Run the RootIQ orchestrator on scenario_1_handoff.json and show me why revenue dropped this month.
```

### Walkthrough (90 seconds)

**1. Upload workbook** (0:45)
- Show the Excel workbook containing 568 rows across 6 sheets (Sales, Inventory, Purchase_Orders, Suppliers, Customer_Feedback).
- Note: The SME Business Data Analyzer has already processed this into a handoff JSON.

**2. Ask the question** (0:50)
- "Why did our revenue drop this month?"
- The Orchestrator identifies: Revenue declined 18.30% (39,975 -> 32,660).

**3. Show data analysis** (0:55)
- The analyzer computed 57 metrics across 6 domains and detected 9 anomalies (5 CRITICAL, 4 HIGH).
- All numbers are deterministic -- no LLM estimation.

**4. Show multiple suspects** (1:05)
- 6 hypotheses generated:
  1. Purchase-Order Approval Bottleneck (HIGH)
  2. Supplier Delay (HIGH)
  3. Inventory Shortage (HIGH)
  4. Customer Dissatisfaction (MEDIUM)
  5. Demand Decline (LOW)
  6. Price Problem (LOW)

**5. Show ranking** (1:20)
- PO Approval Bottleneck ranked #1 (priority score 14.03).
- Key evidence: PO approval time spiked 631% (0.44 -> 3.25 days).

**6. Show self-disproof** (1:30)
- The system challenged its own leading hypothesis across 5 dimensions:
  - Control groups: P002 (+4.04%) and P003 (+2.01%) unaffected -- PASS
  - Timing: PO approval spike preceded stockouts -- PASS
  - Alternatives: Prices unchanged (rules out price), complaints unchanged (rules out dissatisfaction) -- PASS
  - Missing evidence: 2 items identified and retained as unknown -- CAUTION
  - Causal links: 0/4 verified (no event-level timestamps) -- CAUTION
- Verdict: PASS WITH CAUTION

**7. Show validator status** (1:45)
- 8-check Evidence Validator: 6 PASS, 2 PASS WITH CAUTION, 0 FAIL.
- AI Fabrication Check: PASS (no unsupported claims).

**8. Show root-cause chain** (1:55)
```
PO approval delayed (0.44 -> 3.25 days, +631%)
  -> Late replenishment (fulfilment 3.78 -> 7.25 days)
    -> P001 stockouts (0 -> 86.6 hours)
      -> P001 revenue decline (-25.17%)
        -> Overall revenue decline (-18.30%)
```

**9. Show corrective action** (2:05)
- 8 SMART actions generated. Top 2:
  - CA-001 (Critical, 48h): Expedite PO approval -- reduce from 3.25 days to < 1 day.
  - CA-002 (Critical, 24h): Emergency replenishment for P001.
- Each action has an owner, deadline, success metric, and evidence reference.

---

## 2:10-2:35 -- Architecture

RootIQ runs in 5 layers:

1. **Deterministic analysis** -- The SME Business Data Analyzer computes all metrics from code. No AI, no guessing. Every number is reproducible.

2. **Specialist investigators** -- Sales, Inventory/Procurement, and Customer/Operations experts each work within their own domain. No single agent tries to reason across everything.

3. **Self-disproof** -- The leading hypothesis is challenged across 5 dimensions before any claim is made. The system tries to prove itself wrong.

4. **Independent validation** -- A separate 8-check validator reviews the conclusion. It can fail. It does not auto-approve.

5. **Corrective action** -- Only after validation passes does the system generate SMART actions, each tied to evidence.

The key insight: **we separate computation from reasoning, and we separate advocacy from validation.**

---

## 2:35-3:00 -- Value

> "Dashboards show the symptom. RootIQ traces it to a validated cause and turns that cause into action."

Three scenarios tested:
- **Scenario 1:** Revenue decline -> PO approval bottleneck (PASS)
- **Scenario 2:** Profit margin collapse -> Supplier cost increase (PASS)
- **Scenario 3:** Complaints + late deliveries -> Evening staffing shortfall (PASS)

RootIQ correctly identified the root cause in all three scenarios, each representing a completely different business problem. The system did not just sound plausible -- it generated evidence, considered alternatives, challenged its own conclusion, and validated the result.

For an SME owner, this means: **hours of investigation compressed into minutes, with trustworthy, actionable results.**

---

## Demo Backup Plan

If the live WorkBuddy demonstration fails (network, platform, or execution error), use the following pre-generated artifacts:

### 1. Show Saved Investigation Report

Open `rootiq_output/rootiq_final_report.md` -- the 11-section management report from the completed Scenario 1 run. Walk through:
- Section 1: Executive Summary (proposed root cause, financial impact)
- Section 5: Root Cause Analysis (hypothesis ranking table)
- Section 9: Self-Disproof Analysis (5-dimension challenge results)
- Section 10: Corrective Actions (8-action table)

### 2. Show Validation Result

Open `rootiq_output/rootiq_validation_report.json` -- the full validation report. Point to:
- 8-check validator results (6 PASS, 2 PASS WITH CAUTION, 0 FAIL)
- Self-disproof dispositions (3 PASS, 2 CAUTION)
- 24 supported claims, 3 questionable, 2 missing evidence

### 3. Show Corrective Actions

Open `rootiq_output/rootiq_action_register.csv` -- the SMART action register. Highlight:
- CA-001: Expedite PO approval (Critical, 48h, evidence: "PO approval time spike rank #1 anomaly +631.25%")
- CA-002: Emergency P001 replenishment (Critical, 24h, evidence: "P001 stockout hours surge + closing stock decline -60.48%")

### 4. Show Test Results

Open `tests/scenario_1/test_result.md` -- the completed test result showing PASS status, root cause match, and validator confidence.

### 5. Screenshots

If pre-generated screenshots of the WorkBuddy session are available, display them in sequence following the same 9-step walkthrough above.
