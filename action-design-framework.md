# Action Design Framework

This reference defines the principles, rules, and guidelines for designing effective corrective actions that trace directly to validated root causes.

## Core Principle: Root Cause Traceability

Every action in the package must trace directly back to the validated root cause through an unbroken chain:

```
Validated Root Cause
  -> Action designed to address this specific cause
    -> Success metric that confirms the cause is resolved
```

### Traceability Rules

1. **No Orphan Actions**: Every action must state which element of the root cause it addresses. If an action cannot be traced to the root cause, remove it or reframe it.
2. **No Root Cause Without Action**: Every element of the validated root cause must have at least one action addressing it. If a root cause element has no corresponding action, add one or flag the gap.
3. **Traceability Statement**: Each action includes a "Traces To" field naming the specific root cause element it addresses.

### Action Quality Criteria

Every action must satisfy all five criteria:

| Criterion | Description |
|-----------|-------------|
| **Specific** | Names exactly what to do, who does it, and how. No vague directives like "improve the process." |
| **Measurable** | Has a quantifiable success metric (number, percentage, threshold, or binary state). |
| **Achievable** | Realistic given SME resources (budget, personnel, technology). Do not propose enterprise-scale solutions for SME problems. |
| **Time-Bound** | Has a specific deadline or duration. No open-ended actions. |
| **Owned** | Has a named role or function responsible for execution. |

## Priority Levels

| Priority | Definition | Response Time |
|----------|------------|---------------|
| **Critical** | Directly stops ongoing financial loss or operational disruption. Inaction means the problem worsens hourly or daily. | Within 24 hours |
| **High** | Addresses a key contributing factor. Delay beyond the deadline will extend recovery time or risk recurrence. | Within 7 days |
| **Medium** | Strengthens defenses against recurrence. Important but not urgent — the immediate threat is contained. | Within 30 days |
| **Low** | Process optimization or long-term resilience. Valuable but can be scheduled into normal improvement cycles. | Within 90 days |

## Deadline Guidelines

### Immediate Actions (0-24 hours)

Actions at this tier must:
- Address the root cause mechanism directly, not just symptoms.
- Be executable with resources already available (no new hires, no new systems, no procurement).
- Have a clear "done" state (binary or threshold-based).
- Focus on stopping the bleeding and restoring baseline operations.

Examples of appropriate immediate actions:
- Manually overriding a blocked approval workflow.
- Contacting a supplier to expedite a delayed shipment.
- Switching to a backup supplier.
- Issuing a temporary pricing adjustment.
- Pulling forward a scheduled replenishment order.

### Preventive Actions (7-90 days)

Actions at this tier must:
- Modify the process, policy, or system that allowed the root cause to occur.
- Address the structural gap, not just the specific instance.
- Include a sustainability check (how will this be maintained over time?).
- Define the new standard or policy being introduced.

Examples of appropriate preventive actions:
- Adding a secondary supplier to the approved vendor list.
- Implementing an automated stockout alert with escalation rules.
- Revising the PO approval threshold and delegation matrix.
- Creating a standard operating procedure for emergency replenishment.
- Adding a weekly inventory health review to management meetings.

## Success Metric Design

Each action must have a success metric that answers: "How do we know this action worked?"

### Metric Types

| Type | Example | When to Use |
|------|---------|-------------|
| **Binary** | "Backup supplier contract signed" | When the action is a one-time deliverable. |
| **Threshold** | "Stockout hours below 4 hours/month" | When the action targets an ongoing metric. |
| **Trend** | "Revenue recovery to within 5% of baseline by month-end" | When the action aims to reverse a trend. |
| **Ratio** | "Inventory turnover between 6-8x annually" | When the action maintains a healthy operating range. |

### Success Metric Rules

- Must be quantifiable and verifiable from available data.
- Must have a target value (not just "improve" or "increase").
- Must have a measurement frequency (daily, weekly, monthly).
- Must be attributable to the action (not confounded by other changes).

## Action Completeness Checklist

Before finalizing the action package, verify:

- [ ] Every root cause element has at least one corresponding action.
- [ ] Every action traces to a specific root cause element (no orphans).
- [ ] Every action has all five quality criteria (Specific, Measurable, Achievable, Time-Bound, Owned).
- [ ] Every action has a priority level with appropriate response time.
- [ ] Every action has a success metric with a target value and frequency.
- [ ] Immediate actions are executable within 24 hours with existing resources.
- [ ] Preventive actions modify the underlying process or policy, not just the instance.
- [ ] The action register table is complete and internally consistent (no missing fields).
