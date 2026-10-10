# RootIQ Pitch Notes

## One-Line Pitch

> "RootIQ is an autonomous AI investigator for SMEs that finds why a business problem happened, challenges its own conclusion, validates the evidence, and recommends what to do next."

---

## Problem

SMEs operate on thin margins and limited staff. When something goes wrong -- revenue drops, profit margin collapses, complaints spike -- the owner needs to find the root cause fast. But most SMEs don't have a dedicated data analyst. The owner becomes the analyst: pulling spreadsheets, comparing months, checking inventory levels, calling suppliers, and guessing at causes.

This takes hours or days. By the time the cause is found, the damage has compounded: stock is depleted, customers have churned, margins have eroded.

The core problem is not a lack of data. SMEs have plenty of data in their spreadsheets and systems. The problem is a lack of **investigation capacity** -- the ability to systematically trace a symptom back to its root cause across multiple business domains.

---

## Solution

RootIQ takes an SME's business data (Excel/CSV) and one question ("Why did revenue drop?") and performs a complete investigation automatically:

1. **Analyzes** the data deterministically -- every metric computed from code, no AI guessing
2. **Generates** multiple competing hypotheses from specialist investigators
3. **Ranks** the hypotheses by evidence strength
4. **Challenges** its own leading hypothesis through self-disproof
5. **Validates** the conclusion through an independent 8-check validator
6. **Recommends** SMART corrective actions tied to the validated cause

The output is a management-ready report with a validated root cause and an actionable plan -- produced in minutes, not days.

In plain language: **RootIQ does what a good business analyst would do, but faster, more rigorously, and without skipping the hard steps.**

---

## Differentiator

### Not a Dashboard

Dashboards show **what changed**. RootIQ explains **why it changed**. A dashboard says "revenue dropped 18%." RootIQ says "revenue dropped because the PO approval process delayed replenishment, causing Product A stockouts, which reduced Product A sales."

### Not a Generic Chatbot

A generic chatbot (ChatGPT, etc.) can read an Excel file and produce a plausible-sounding analysis. But it has no self-correction mechanism, no independent validation, no deterministic computation layer, and no structured investigation protocol. It can -- and does -- hallucinate numbers.

RootIQ separates computation from reasoning:

| Generic Chatbot | RootIQ |
|---|---|
| Single AI agent does everything | Deterministic analyzer + specialist investigators + validator |
| May hallucinate numbers | Every metric computed from code, audited |
| First plausible answer wins | Multiple competing hypotheses, ranked by evidence |
| No self-correction | Mandatory self-disproof of leading hypothesis |
| No independent validation | 8-check Evidence Validator can FAIL |
| No structured output | Management report + SMART action register |
| No audit trail | Full investigation trace recorded |

### Self-Disproof

The single most important differentiator: **RootIQ actively tries to disprove its own leading hypothesis before making a claim.** This is not a feature bolted on -- it is a mandatory step in the workflow. No root cause is proposed without a 5-dimension challenge:

1. Control groups (are unaffected entities truly unaffected?)
2. Timing alignment (does cause precede effect?)
3. Alternative explanations (what else could explain this?)
4. Missing evidence (what don't we know?)
5. Causal link strength (are the chain links verified?)

### Independent Validation

The Evidence Validator is a separate component from the hypothesis engine. It can return FAIL. It checks for AI fabrication, math errors, and unsupported claims. The system does not auto-approve.

### Evidence-Based Corrective Action

Actions are generated only after validation passes, and each action includes an evidence reference tying it to the validated cause. No actions for unvalidated hypotheses.

---

## Business Value

- **Saves investigation time:** Hours of manual analysis compressed into minutes of automated workflow.
- **Reduces dependence on analysts:** SMEs without dedicated data staff get investigation-quality results.
- **Helps owners act faster:** Validated root cause + SMART actions mean the owner can start fixing the problem immediately, not after days of investigation.
- **Makes AI conclusions more trustworthy:** Deterministic computation + self-disproof + independent validation = AI conclusions that can be audited and trusted. No black-box answers.

---

## Likely Q&A

### 1. How is this different from ChatGPT analyzing Excel?

ChatGPT uses a single AI agent to both compute and reason. It may hallucinate numbers, has no self-correction, and produces no auditable trail. RootIQ separates deterministic computation (code, no AI) from AI reasoning (hypothesis generation, self-disproof, validation). Every number is reproducible. Every conclusion is challenged. Every claim is auditable.

### 2. What prevents hallucinations?

Three layers: (1) The Data Analyzer is LLM-free -- all metrics are computed from deterministic Python code. (2) The Evidence Validator includes an AI Fabrication Check (check #8) that verifies no unsupported claims exist. (3) The self-disproof module identifies missing evidence and retains it as "unknown" rather than allowing the system to fill gaps with estimates.

### 3. Why WorkBuddy?

WorkBuddy provides the infrastructure we needed: Skills (deterministic code execution), Experts (specialist agent roles), and an agent orchestration layer. The WorkBuddy Skill system let us package the Data Analyzer as a reusable, LLM-free tool. The Expert system let us create domain specialists (Sales Investigator). The agent loop let us build the orchestrator on top.

### 4. Can it work with real SME data?

Yes. The Data Analyzer accepts any Excel workbook or CSV files with the expected sheet structure (Sales, Inventory, Purchase_Orders, Suppliers, Customer_Feedback, Operations). It validates the schema, parses 7 date formats, handles missing optional sheets, and reports data quality issues. The analysis is generic -- it works on any SME dataset with these tables.

### 5. Why use synthetic data in the demo?

Synthetic data gives us a known ground truth. We designed three scenarios with planted root causes (PO approval bottleneck, supplier cost increase, Evening staffing shortfall) so we could verify that RootIQ correctly identifies the cause. With real SME data, we wouldn't know the true root cause in advance, making it impossible to validate the system's accuracy. The synthetic data is realistic in structure -- it uses the same columns and data types as real SME systems.

### 6. What happens if the evidence is insufficient?

The system says so explicitly. The self-disproof module retains missing evidence as "unknown" rather than fabricating values. If the Evidence Validator returns FAIL, the system reports "No confirmed root cause" and lists the validation failures and missing evidence. The final report includes all gaps transparently. RootIQ would rather say "I don't know" than make an unsupported claim.

### 7. Why not use one agent?

A single agent conflates computation with reasoning, advocacy with validation, and domain expertise across business areas. By separating into specialists, each agent works within its evidence domain and cannot conflate symptoms. The Evidence Validator is separate from the hypothesis engine -- it can reject the conclusion. This separation of concerns is the core architectural principle that makes the system trustworthy.

### 8. How do you validate the root cause?

The Evidence Validator runs 8 independent checks: Data Support, Chronology, Causality vs. Symptom, Alternative Explanations, Contradiction Check, Chain Validation, Math Verification, and AI Fabrication Check. Each returns PASS, PASS WITH CAUTION, or FAIL. The validator can fail -- it does not auto-approve. Additionally, the self-disproof module challenges the leading hypothesis across 5 dimensions before the validator even runs.

### 9. How scalable is the system?

The Data Analyzer scales with data size -- it's pandas-based and handles the tested workbooks (300-600 rows) in under a second. The Teammate2 engine is dependency-free Python. The orchestrator adds minimal overhead. For larger datasets, the bottleneck would be the pandas operations in the analyzer, which can be optimized or moved to a database-backed implementation. The investigation logic itself (hypothesis generation, self-disproof, validation) does not scale with data size -- it depends on the number of anomalies and hypotheses, which is typically bounded.

### 10. What would you build next with more time?

- Run the full orchestrator pipeline on Scenarios 2 and 3 (currently only Scenario 1 has full end-to-end validation)
- Add event-level timestamp linking to upgrade causal chain links from UNVERIFIED to SUPPORTED (this would raise confidence from LOW to HIGH)
- Add a validator rejection test -- intentionally feed an unsupported conclusion and verify the validator returns FAIL
- Support more data domains (HR, Finance, Logistics) and more anomaly rule types
- Build a conversational interface where the owner can ask follow-up questions and drill into specific evidence
- Add counterfactual impact estimation (not just actual revenue loss, but projected recovery if corrective actions are implemented)

---

## Team Responsibility

### Teammate 1: Data Analyzer / Metrics / Evidence

- Built the SME Business Data Analyzer (1,599 lines, 28+ metrics, 19 anomaly rules)
- Designed the calculation specification (28-metric spec with formulas and thresholds)
- Created the standard evidence format (handoff JSON schema)
- Ran analysis on all 3 scenarios
- Performed independent data quality audit (108 cross-validation checks, 0 errors)

### Teammate 2: Investigation / Hypotheses / Validation

- Built the Teammate2 reasoning engine (hypothesis ranking, causal chain, evidence validation)
- Implemented the 5-dimension self-disproof module
- Designed the 8-check Evidence Validator
- Created the Sales Performance Investigator Expert (7-step investigation protocol)
- Validated all 3 scenarios (correct root cause identified in all)

### Teammate 3: Orchestration / Corrective Action / Final Experience

- Built the RootIQ Orchestrator (14-step end-to-end workflow)
- Created the RootIQ Mapper (analyzer-to-engine translation layer)
- Implemented the Corrective Action Executor (SMART action generation)
- Generated the 11-section management report and 7 output artifacts
- Created all project documentation (architecture, workflow, demo script, test results, GitHub docs)
