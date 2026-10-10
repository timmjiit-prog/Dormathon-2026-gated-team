# Investigation Methodology

This reference defines the structured analytical methodology for RootIQ Orchestrator investigations, including hypothesis generation, causal chain construction, evidence validation, and confidence ranking.

## Hypothesis Generation

### Requirements

Generate a minimum of THREE plausible hypotheses for the observed business problem. Each hypothesis must be:

1. **Plausible** — Supported by at least one data signal or pattern from the analysis phase.
2. **Specific** — Names the mechanism, not just the symptom (e.g., "Supplier delivery delays caused stockouts that reduced sell-through" not "supply chain issues").
3. **Testable** — Can be confirmed or refuted using available datasets or logical deduction.
4. **Distinct** — Each hypothesis offers a meaningfully different explanation, not a restatement of another.

### Hypothesis Evaluation Criteria

Score each hypothesis across four dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Data Alignment | 35% | How well the hypothesis is supported by quantitative evidence from the datasets. |
| Logical Coherence | 25% | Whether the causal mechanism is internally consistent and follows sound business logic. |
| Explanatory Power | 25% | How much of the observed variance the hypothesis accounts for (does it explain the full magnitude of the problem?). |
| Refutability | 15% | Whether contrary evidence was examined and the hypothesis survived falsification attempts. |

Compute a weighted score (0-100) for each hypothesis and rank them. The top-ranked hypothesis becomes the primary root cause candidate for validation.

### Hypothesis Template

For each hypothesis, document:

```
Hypothesis [N]: [Concise statement of the proposed root cause]
  Supporting Evidence: [Specific data points, metrics, patterns]
  Contrary Evidence: [Data that weakens or contradicts this hypothesis]
  Explanatory Gap: [What this hypothesis does NOT explain]
  Score: [Weighted 0-100]
```

## Causal Chain Construction

### Structure

Every root cause must be traced through a complete causal chain:

```
Observed Problem
  → Contributing Factor(s)
    → Intermediate Cause(s)
      → Underlying Root Cause
```

### Definitions

- **Observed Problem**: The business symptom that triggered the investigation (e.g., "34.8% revenue drop in October").
- **Contributing Factor**: A measurable condition or event that directly contributed to the observed problem (e.g., "Order volume decreased 28% while average order value declined 9%").
- **Intermediate Cause**: The mechanism that produced the contributing factor (e.g., "Top 3 product SKUs were out of stock for 12 of 30 days, accounting for 65% of lost orders").
- **Underlying Root Cause**: The fundamental reason that, if resolved, would prevent recurrence (e.g., "Supplier B's production capacity was reduced by 40% due to equipment failure, and no secondary supplier was contracted as backup").

### Construction Rules

1. **Trace Forward**: Start from the root cause and walk forward to verify it logically produces the observed problem at each step.
2. **Trace Backward**: Start from the observed problem and ask "Why?" at each level until reaching a cause that is actionable and fundamental.
3. **Quantify Each Link**: Every link in the chain must include a quantified metric (percentage, absolute number, dollar amount, or time period).
4. **No Gaps**: The chain must be unbroken — no link should require an unsupported leap of logic.
5. **Single Primary Chain**: Identify ONE primary causal chain. Secondary or contributing chains may be noted but must be clearly labeled as secondary.

## Evidence Validation

### Validation Protocol

Before finalizing the root cause, validate it against the following checks:

1. **Data Sufficiency Check**: Is the conclusion supported by data from at least two independent data sources or analytical perspectives?
2. **Magnitude Check**: Does the root cause explain the FULL magnitude of the observed problem? If the root cause accounts for only 60% of the revenue drop, note the residual and investigate or flag it.
3. **Timeline Check**: Does the timeline of the root cause precede and align with the onset of the observed problem?
4. **Alternative Elimination**: Were alternative hypotheses actively examined and refuted with evidence (not just by absence of supporting data)?
5. **Consistency Check**: Does the conclusion remain consistent when examined from different analytical angles (e.g., top-down financial view vs. bottom-up operational view)?

### Validation Result

Document the validation outcome as:

- **VALIDATED** — All five checks pass. The root cause is confirmed.
- **PARTIALLY VALIDATED** — 3-4 checks pass. Note which checks failed and why.
- **UNVALIDATED** — Fewer than 3 checks pass. Flag for additional data collection.

## Confidence Ranking

### Criteria

| Level | Criteria |
|-------|----------|
| **HIGH** | Root cause is VALIDATED. All five checks pass. Causal chain is complete and quantified at every link. The root cause explains >=90% of the observed impact. Multiple independent data sources agree. |
| **MEDIUM** | Root cause is PARTIALLY VALIDATED. 3-4 checks pass. Causal chain is complete but some links have weaker quantification. The root cause explains 70-90% of the observed impact. |
| **LOW** | Root cause is UNVALIDATED or fewer than 3 checks pass. Causal chain has gaps. The root cause explains <70% of the observed impact. Additional investigation is recommended. |

### Application

- State confidence level explicitly in the final report.
- For MEDIUM confidence, list specific gaps that would raise it to HIGH.
- For LOW confidence, recommend additional data collection or investigation steps.
