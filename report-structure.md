# Management Investigation Report Structure

This reference defines the mandatory structure and content requirements for the final management investigation report produced by RootIQ Orchestrator.

## Report Sections

### 1. Executive Summary

A concise one-page summary for senior management.

- **Problem Statement**: What happened, when, and the magnitude (one sentence).
- **Root Cause**: The validated root cause (one to two sentences).
- **Financial Impact**: Total quantified loss (one line).
- **Key Actions**: Top 3 immediate corrective actions (bullet list).
- **Confidence Level**: HIGH / MEDIUM / LOW.

### 2. Investigation Scope

- **Business Issue Investigated**: Full description of the observed problem.
- **Affected Metrics**: Specific metrics and their change (e.g., "Revenue: -34.8% MoM", "Gross Margin: -5.2pp").
- **Investigation Period**: Date range under analysis.
- **Datasets Analyzed**: List of datasets provided and their scope (rows, columns, time coverage).
- **Specialist Areas Engaged**: Which specialist analyses were performed.

### 3. Data Analysis Summary

Summarize the factual findings from the data analysis phase. This section presents WHAT the data shows, not WHY.

- **Key Metric Changes**: Table of before/after comparisons for all affected metrics.
- **Segment Breakdown**: Performance by product category, customer segment, channel, region, or time period.
- **Anomaly Detection**: Outliers, unexpected patterns, or statistical anomalies identified.
- **Trend Analysis**: Time-series observations showing when changes began and how they evolved.

### 4. Specialist Findings

For each specialist area engaged, summarize:

- **Area**: Sales / Inventory & Procurement / Customer & Operations.
- **Key Findings**: 3-5 bullet points of the most important factual discoveries.
- **Data Signals**: Specific metrics or patterns that are significant.
- **Preliminary Assessment**: The specialist's initial interpretation (not the final root cause).

### 5. Hypothesis Evaluation

Present all evaluated hypotheses using the standard template:

- List each hypothesis (minimum 3).
- For each: supporting evidence, contrary evidence, explanatory gap, and weighted score.
- State which hypothesis was selected as the primary root cause candidate and why.

### 6. Causal Chain Analysis

Present the complete, validated causal chain:

```
Observed Problem: [Description + quantified impact]
  |
  +-- Contributing Factor 1: [Description + quantified metric]
  |     |
  |     +-- Intermediate Cause 1A: [Description + quantified metric]
  |           |
  |           +-- Underlying Root Cause: [Description + quantified metric]
  |
  +-- Contributing Factor 2: [Description + quantified metric] (if applicable)
```

- Include the quantified impact at each link.
- Note any secondary causal chains as "Secondary Finding."
- State the validation result (VALIDATED / PARTIALLY VALIDATED / UNVALIDATED).

### 7. Financial Impact Quantification

A detailed breakdown of the financial loss:

- **Total Impact**: Aggregate financial loss (revenue, margin, or relevant metric) in absolute currency and percentage.
- **Impact Decomposition**: Break down the total by contributing factor (e.g., "Lost sales due to stockouts: ¥X (Y% of total)", "Price discounting to clear inventory: ¥X (Y% of total)").
- **Direct vs. Indirect**: Separate direct losses (e.g., lost revenue) from indirect costs (e.g., expedited shipping, customer compensation, brand impact estimates).
- **Period Impact**: Loss attributable to the investigation period and projected forward impact if uncorrected.

### 8. Corrective Actions (Immediate)

Actions to be executed within 0-30 days to stop the bleeding:

For each action:
- **Action ID**: CA-001, CA-002, etc.
- **Action**: Specific, actionable description.
- **Objective**: What this action achieves.
- **Owner**: Recommended responsible function or role.
- **Timeline**: Target completion date or duration.
- **Success Metric**: How to confirm the action worked.
- **Estimated Cost**: Cost to implement (if applicable).
- **Priority**: Critical / High / Medium.

### 9. Preventive Plans

Actions to be executed within 30-90 days to prevent recurrence:

For each plan:
- **Plan ID**: PP-001, PP-002, etc.
- **Plan**: Description of the systemic change or process improvement.
- **Risk Addressed**: Which root cause element this prevents.
- **Owner**: Recommended responsible function or role.
- **Timeline**: Target completion date.
- **Dependencies**: Any prerequisites or cross-functional coordination needed.
- **Investment Required**: Resources, budget, or technology needed.

### 10. Monitoring KPIs

Ongoing metrics to detect recurrence or measure recovery:

For each KPI:
- **KPI Name**: Descriptive name.
- **Definition**: How it is calculated.
- **Target**: Target value or threshold.
- **Alert Threshold**: Value that triggers investigation.
- **Frequency**: Daily / Weekly / Monthly.
- **Data Source**: Where the data comes from.
- **Owner**: Who is responsible for monitoring.

### 11. Action Register

A consolidated table of all actions across corrective and preventive categories:

| ID | Category | Action | Owner | Priority | Start Date | Due Date | Status | Success Metric |
|----|----------|--------|-------|----------|------------|----------|--------|----------------|
| CA-001 | Corrective | ... | ... | Critical | ... | ... | Not Started | ... |
| PP-001 | Preventive | ... | ... | High | ... | ... | Not Started | ... |

## Formatting Guidelines

- Use professional business report formatting.
- Include a table of contents for reports exceeding 5 pages.
- All currency values in local currency with appropriate formatting.
- All percentages to one decimal place.
- All tables should have clear headers and alignment.
- Use bullet points for lists and numbered sequences for procedures.
- Bold key findings and critical actions for scannability.
