---
name: rootiq-orchestrator
description: "Autonomous SME Root Cause Investigation Orchestrator that coordinates end-to-end investigation, specialist analysis, evidence validation, and corrective action generation from a single business goal. This skill should be used when a user reports a significant business problem (revenue drop, margin collapse, inventory bottleneck, operational failure) and requests a complete autonomous investigation using structured business datasets. Trigger phrases include 'investigate revenue drop', 'find root cause', 'autonomous investigation', 'why did revenue decline', 'analyze business failure', 'root cause analysis', or any request to autonomously diagnose and produce a full management action package for an SME business problem."
agent_created: true
---

# RootIQ Orchestrator

## Overview

RootIQ Orchestrator is an autonomous investigation coordinator that transforms a single business problem statement into a complete, validated management action package. It orchestrates a structured 10-step workflow spanning goal interpretation, data analysis, specialist delegation, hypothesis generation, causal chain construction, evidence validation, impact quantification, and corrective action generation.

The orchestrator does not perform raw data analysis itself — it delegates to specialist agents and integrates their findings into a coherent, validated conclusion. The final deliverable is a comprehensive management investigation report containing the verified root cause, causal chain, financial impact, corrective actions, preventive plans, monitoring KPIs, and an action register.

## When to Use

Activate this skill when ALL of the following are present:

- A significant, quantified business problem is reported (e.g., "34.8% revenue drop").
- Structured business datasets are available for analysis (sales, inventory, procurement, customer data).
- The user expects a complete investigation package, not just a data summary.
- The user uses trigger phrases like "autonomously investigate", "find the root cause", or "produce the complete management action package."

Do NOT activate for simple data lookups, single-metric questions, or when the user only wants a data summary without root cause analysis.

## Investigation Workflow

Execute the following 10 steps in sequence. Each step feeds into the next. Do not skip steps. Document progress at each stage so the user can follow the investigation as it unfolds.

### Step 1: Understand the Goal

Identify and document the following before any analysis begins:

- **Business Issue**: What is the reported problem? (e.g., "SME experienced a 34.8% revenue drop this month")
- **Affected Metrics**: Which specific KPIs are impacted? (e.g., revenue, gross margin, order volume, customer count)
- **Investigation Period**: What time period is under analysis? Identify the comparison baseline (e.g., current month vs. previous month, or vs. same period last year).
- **Magnitude**: How severe is the problem? Quantify the deviation from expected performance.
- **Business Context**: What is the company type, industry, size, and any known recent events that may be relevant?

Present the goal summary to the user for confirmation before proceeding to planning.

### Step 2: Plan the Investigation

Determine which investigation areas are relevant based on the business issue and available datasets. The standard investigation areas are:

| Area | Relevant When |
|------|---------------|
| Sales | Revenue, pricing, volume, or product mix changes are involved. |
| Inventory | Stockouts, overstock, turnover, or supply disruptions are suspected. |
| Procurement | Supplier issues, cost changes, or delivery problems may be contributing. |
| Customers | Churn, acquisition, behavior shifts, or satisfaction issues are relevant. |

For each selected area, note which datasets will be analyzed and what specific questions the analysis should answer.

Load `references/specialist-roles.md` to review the specialist scope definitions and confirm which specialists will be engaged in Step 4.

### Step 3: Execute Data Analysis

Analyze the uploaded datasets to extract factual findings. This step produces WHAT the data shows — not WHY.

Perform the following analytical tasks on all relevant datasets:

1. **Metric Calculation**: Compute all affected metrics for the investigation period and baseline period. Present as a before/after comparison table.
2. **Segmentation Analysis**: Break down metrics by product category, customer segment, sales channel, region, and time period to identify where the problem is concentrated.
3. **Trend Analysis**: Plot or describe the time-series behavior to identify when the problem began and how it evolved.
4. **Anomaly Detection**: Identify outliers, unexpected patterns, or statistical anomalies in the data.
5. **Correlation Scan**: Check for correlations between metrics (e.g., did stockouts correlate with revenue decline in specific product categories?).

Document all findings as structured factual statements with supporting numbers. These findings will be passed to specialists in the next step.

### Step 4: Delegate Investigation

Send the factual data findings to specialist agents for domain-specific interpretation. Launch specialist agents using the Agent tool in parallel where possible.

For each specialist area identified in Step 2:

1. **Prepare the delegation package**: Business context (from Step 1), relevant data findings (from Step 3), and the specific analysis task.
2. **Launch the specialist agent**: Use the Agent tool with a descriptive prompt that includes the data findings and asks for domain interpretation, contributing factors, quantified impact, and preliminary hypotheses.
3. **Collect results**: Gather key findings, quantified impacts, and preliminary hypotheses from each specialist.

Refer to `references/specialist-roles.md` for each specialist's scope, key analysis areas, and delegation focus.

**Delegation prompt template** (adapt per specialist):

```
You are a [Specialist Role] analyzing an SME business problem.

Business Context: [Problem statement, affected metrics, investigation period]

Data Findings Relevant to Your Domain:
[Paste the specific analytical results from Step 3 that fall within this specialist's scope]

Your Task:
1. Identify the top 3-5 significant findings within your domain.
2. Quantify the impact of each finding (dollar amount or percentage).
3. Propose 1-2 preliminary root cause hypotheses specific to your domain.
4. Note any patterns that may connect to another specialist's domain.

Return your analysis in structured format.
```

Launch all specialist agents simultaneously to maximize efficiency. Collect all results before proceeding to hypothesis generation.

### Step 5: Generate Hypotheses

Synthesize the specialist findings and data analysis results into a minimum of THREE plausible root cause hypotheses.

Load `references/investigation-methodology.md` and follow the Hypothesis Generation section:

1. **Synthesize**: Combine insights across all specialist domains. Look for convergence (multiple specialists pointing to the same cause) and divergence (conflicting interpretations).
2. **Generate**: Formulate at least three distinct, plausible, specific, and testable hypotheses using the hypothesis template.
3. **Evaluate**: Score each hypothesis across the four dimensions (Data Alignment 35%, Logical Coherence 25%, Explanatory Power 25%, Refutability 15%).
4. **Rank**: Order hypotheses by weighted score. The top-ranked hypothesis becomes the primary root cause candidate.

Document all hypotheses with their scores and present them before proceeding to causal chain construction.

### Step 6: Build Causal Chains

For the top-ranked hypothesis, construct a complete causal chain tracing from the observed problem back to the underlying root cause.

Follow the Causal Chain Construction rules in `references/investigation-methodology.md`:

```
Observed Problem
  -> Contributing Factor(s) [with quantified metrics]
    -> Intermediate Cause(s) [with quantified metrics]
      -> Underlying Root Cause [with quantified metrics]
```

Rules:
- Trace both forward (root cause -> observed problem) and backward (observed problem -> root cause) to verify logical consistency.
- Quantify every link with a specific metric (percentage, absolute number, dollar amount, or time period).
- Ensure no gaps in the chain — each link must logically produce the next.
- Identify ONE primary causal chain. Note secondary chains separately if they exist.
- Verify the chain accounts for the full magnitude of the observed problem. If there is a residual (unexplained portion), quantify it.

### Step 7: Validate

Submit the proposed root cause and causal chain to evidence validation before finalizing.

Follow the Evidence Validation protocol in `references/investigation-methodology.md` and execute all five checks:

1. **Data Sufficiency Check**: Is the conclusion supported by at least two independent data sources or analytical perspectives?
2. **Magnitude Check**: Does the root cause explain the full magnitude of the problem? Quantify any residual.
3. **Timeline Check**: Does the root cause precede and align with the onset of the observed problem?
4. **Alternative Elimination**: Were alternative hypotheses actively examined and refuted with specific evidence?
5. **Consistency Check**: Does the conclusion hold when examined from different analytical angles?

Document the validation result as VALIDATED, PARTIALLY VALIDATED, or UNVALIDATED, with specific notes on which checks passed or failed.

**Validation approach**: Re-examine the raw data findings and specialist outputs to challenge the proposed conclusion. Actively look for evidence that would refute the root cause. If refuting evidence is found and cannot be explained, return to Step 5 and re-evaluate hypotheses.

### Step 8: Integrate and Rank

Finalize the root cause and assign a confidence level based on the validation results.

Follow the Confidence Ranking criteria in `references/investigation-methodology.md`:

- **HIGH**: Root cause VALIDATED. All five checks pass. Causal chain complete and quantified at every link. Explains >=90% of observed impact. Multiple independent sources agree.
- **MEDIUM**: Root cause PARTIALLY VALIDATED. 3-4 checks pass. Causal chain complete but some links have weaker quantification. Explains 70-90% of observed impact.
- **LOW**: Root cause UNVALIDATED. Fewer than 3 checks pass. Causal chain has gaps. Explains <70% of observed impact.

For MEDIUM confidence: list specific gaps that would raise it to HIGH.
For LOW confidence: recommend additional data collection or investigation steps.

### Step 9: Quantify Impact

Calculate the exact financial impact of the root cause.

Decompose the total impact:

1. **Total Impact**: Aggregate financial loss in absolute currency and percentage change.
2. **Impact by Contributing Factor**: Break down the total loss by each contributing factor in the causal chain. Each factor's impact should be quantified as both an absolute amount and a percentage of total impact.
3. **Direct vs. Indirect Costs**: Separate direct losses (e.g., lost revenue from stockouts) from indirect costs (e.g., expedited shipping, customer compensation, estimated brand impact).
4. **Period Impact**: Loss attributable to the investigation period specifically.
5. **Projected Forward Impact**: Estimated ongoing loss per month if the root cause remains uncorrected.

Present the impact as a structured table. All currency values should use the appropriate local currency symbol.

### Step 10: Execute Corrective Action Generation

Produce the complete corrective action package with four components:

#### A. Immediate Corrective Actions (0-30 days)

Actions to stop the immediate bleeding. For each action document:
- Action ID (CA-001, CA-002, ...)
- Specific action description
- Objective
- Recommended owner (function or role)
- Target timeline
- Success metric
- Estimated cost (if applicable)
- Priority (Critical / High / Medium)

Generate at least 3-5 immediate corrective actions directly targeting the root cause and its intermediate causes.

#### B. Preventive Plans (30-90 days)

Systemic changes to prevent recurrence. For each plan document:
- Plan ID (PP-001, PP-002, ...)
- Description of the systemic change or process improvement
- Which root cause element it prevents
- Recommended owner
- Timeline
- Dependencies
- Investment required

Generate at least 2-3 preventive plans addressing the underlying root cause, not just the symptoms.

#### C. Monitoring KPIs

Ongoing metrics to detect recurrence and measure recovery. For each KPI document:
- KPI name
- Definition (calculation method)
- Target value
- Alert threshold (value that triggers investigation)
- Monitoring frequency (Daily / Weekly / Monthly)
- Data source
- Owner

Define at least 4-6 monitoring KPIs covering both the affected metrics and the root cause indicators.

#### D. Action Register

Consolidate all actions (corrective + preventive) into a single register table:

| ID | Category | Action | Owner | Priority | Start Date | Due Date | Status | Success Metric |
|----|----------|--------|-------|----------|------------|----------|--------|----------------|

All actions start with status "Not Started."

## Final Report Generation

After completing all 10 steps, compile the complete management investigation report.

Load `references/report-structure.md` and follow the mandatory report structure. The report must contain all 11 sections:

1. Executive Summary
2. Investigation Scope
3. Data Analysis Summary
4. Specialist Findings
5. Hypothesis Evaluation
6. Causal Chain Analysis
7. Financial Impact Quantification
8. Corrective Actions (Immediate)
9. Preventive Plans
10. Monitoring KPIs
11. Action Register

Present the final report to the user using the `present_files` tool so it is viewable and downloadable.

## Key Principles

- **Autonomy**: Operate without requiring user input between steps unless a critical decision point is reached (e.g., goal confirmation in Step 1).
- **Evidence-First**: Every conclusion must be backed by quantified data, not assumptions or general business knowledge.
- **Transparency**: Document the investigation process so the user can follow the reasoning chain from problem to conclusion.
- **Completeness**: The final deliverable must be a self-contained management package that a decision-maker can act on immediately.
- **Honesty About Uncertainty**: If confidence is MEDIUM or LOW, state it clearly. Do not present uncertain conclusions as definitive.

## Bundled References

The following reference files provide detailed methodology and templates. Load them at the indicated steps:

| Reference File | Load At | Content |
|----------------|---------|---------|
| `references/investigation-methodology.md` | Steps 5-8 | Hypothesis generation criteria, causal chain construction rules, evidence validation protocol, confidence ranking rubric. |
| `references/specialist-roles.md` | Steps 2 & 4 | Specialist role definitions, scope, key analysis areas, delegation prompt template, and integration rules. |
| `references/report-structure.md` | Final Report | Mandatory 11-section report structure with content requirements and formatting guidelines. |
