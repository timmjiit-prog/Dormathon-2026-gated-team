---
name: corrective-action-executor
description: "Turns validated investigation findings and root causes into actionable, realistic business recovery packages for SME management. This skill should be used after a root cause investigation has been completed and the validated root cause is available. It generates immediate 24-hour actions, preventive process updates, KPI monitoring thresholds, action register tables, and ready-to-send communication drafts. Trigger when a user provides a validated root cause statement and requests corrective actions, recovery plans, action packages, or communication drafts following a business investigation."
agent_created: true
---

# Corrective Action Executor

## Overview

The Corrective Action Executor transforms validated root cause findings into a complete, actionable business recovery package. Given a validated root cause (typically the output of an investigation skill like RootIQ Orchestrator), it produces five deliverables: immediate actions executable within 24 hours, preventive process changes, KPI monitoring controls with warning and critical thresholds, a consolidated action register table, and ready-to-send professional communication drafts for managers, suppliers, and team members.

The core rule governing this skill: **every action must trace directly back to the validated root cause.** No action is generated that cannot be linked to a specific element of the root cause finding.

## When to Use

Activate this skill when ALL of the following are present:

- A validated root cause is available (from an investigation, root cause analysis, or direct user statement).
- The user requests actionable next steps, a recovery package, or corrective actions.
- The context is SME business management (operations, sales, inventory, procurement, customer service).

Do NOT activate for:
- General business advice or planning unrelated to a specific root cause.
- Situations where the root cause has not yet been identified or validated.
- Pure data analysis requests without a root cause finding.

## Input Requirements

The skill expects the following input from the user or preceding investigation:

| Input | Required | Description |
|-------|----------|-------------|
| Validated Root Cause | Yes | A clear statement of the root cause, ideally with confidence level. |
| Financial Impact | Recommended | Quantified loss or impact associated with the problem. |
| Causal Chain | Recommended | The chain from observed problem to root cause, if available. |
| Business Context | Recommended | Company type, industry, size, and any operational constraints. |
| Affected Metrics | Recommended | The specific KPIs that were impacted by the problem. |

If required input is missing, request it from the user before proceeding. If recommended input is missing, proceed with reasonable assumptions and note them.

## Workflow

Execute the following 5 steps in sequence. Each step builds on the validated root cause. The traceability rule applies throughout: every action must trace to the root cause.

### Step 1: Immediate Action (Within 24 Hours)

Generate actions that management must execute within 24 hours to stop ongoing damage and restore baseline operations.

Load `references/action-design-framework.md` and follow the Immediate Actions guidelines.

For each immediate action, document:

- **Action ID**: IA-001, IA-002, etc.
- **Action**: Specific, actionable description (what exactly to do).
- **Traces To**: Which element of the validated root cause this addresses.
- **Objective**: What this action achieves in the immediate term.
- **Owner**: Recommended role or function responsible (specific job title, not "someone").
- **Deadline**: Within 24 hours (state the specific clock deadline, e.g., "By 5:00 PM today").
- **Success Metric**: How to confirm the action worked (binary, threshold, or trend).
- **Priority**: Always Critical for immediate actions.
- **Resources Needed**: What is required to execute (must be available with existing resources — no new procurement, hiring, or system implementation).

Design guidelines:
- Generate 3-7 immediate actions depending on the complexity of the root cause.
- Each action must directly address the root cause mechanism, not just symptoms.
- Actions must be executable with existing resources (personnel, budget, systems available today).
- If the root cause cannot be fully resolved in 24 hours (common), the immediate actions should contain the damage while preventive actions (Step 2) address the structural fix.
- State clearly which actions are "stopping the bleeding" vs. "beginning the fix."

### Step 2: Preventive Action (Process/Policy Changes)

Generate actions that modify the underlying process, policy, or system to prevent the root cause from recurring.

Load `references/action-design-framework.md` and follow the Preventive Actions guidelines.

For each preventive action, document:

- **Action ID**: PA-001, PA-002, etc.
- **Action**: Description of the process or policy change.
- **Traces To**: Which element of the validated root cause this prevents.
- **Risk Addressed**: What specific recurrence scenario this eliminates.
- **Owner**: Recommended role or function responsible.
- **Deadline**: 7-90 days (state specific target date).
- **Priority**: High or Medium (based on recurrence risk severity).
- **New Standard**: What the new process, policy, or threshold will be.
- **Sustainability Check**: How this change will be maintained over time (review frequency, ownership).
- **Investment Required**: Resources, budget, or technology needed (if any).

Design guidelines:
- Generate 2-5 preventive actions addressing each structural gap identified in the root cause.
- Preventive actions must modify the process, not just address the specific instance.
- Include at least one action that creates a new standard operating procedure or policy if one was missing.
- Include at least one action that introduces a checkpoint or escalation rule if the root cause involved a process failure that went undetected.
- Consider supplier diversification, inventory policy changes, approval workflow modifications, or system alerts as appropriate to the root cause.

### Step 3: Monitoring Control (KPI Thresholds)

Define the monitoring framework that will detect recurrence early and measure recovery.

For each monitoring KPI, document:

- **KPI Name**: Descriptive name.
- **Traces To**: Which root cause indicator this KPI monitors.
- **Definition**: How the KPI is calculated (formula or calculation method).
- **Normal Range**: The healthy operating range (min-max or target value).
- **Warning Threshold**: The value that triggers proactive investigation (before the problem recurs).
- **Critical Threshold**: The value that triggers immediate escalation and emergency action.
- **Measurement Frequency**: How often the KPI is checked (hourly, daily, weekly, monthly).
- **Data Source**: Where the data comes from (system, report, manual check).
- **Owner**: Who is responsible for monitoring and responding.
- **Escalation Path**: Who to notify when the warning or critical threshold is breached.

Design guidelines:
- Generate 3-6 monitoring KPIs covering both the directly affected metrics and leading indicators of the root cause.
- Warning thresholds must be set BEFORE the problem level — the goal is early detection, not confirmation that the problem has returned.
- Critical thresholds should correspond to the level at which the problem was observed (the level that triggered the original investigation).
- Include at least one leading indicator (a metric that changes BEFORE the problem manifests) and one lagging indicator (a metric that confirms the problem has occurred).
- Define clear escalation paths for both warning and critical threshold breaches.

### Step 4: Action Register Table

Consolidate all actions from Steps 1-3 into a single, structured action register.

The action register must include ALL actions (immediate, preventive, and monitoring setup) in one table:

| ID | Action | Traces To | Owner/Role | Priority | Recommended Deadline | Success Metric | Status |
|----|--------|-----------|------------|----------|----------------------|----------------|--------|

Rules:
- Every row must have all fields completed — no empty cells.
- IDs follow the convention: IA-xxx (immediate), PA-xxx (preventive). Monitoring KPI setup actions use MK-xxx.
- Priority values: Critical, High, Medium, Low.
- Status starts as "Not Started" for all actions.
- Sort by priority (Critical first, then High, Medium, Low) and then by deadline (earliest first).
- The "Traces To" column is mandatory — it is the core traceability mechanism ensuring no action exists without a root cause link.

### Step 5: Communication Draft

Produce ready-to-send professional communications tailored to the key stakeholders.

Load `references/communication-templates.md` and select the appropriate templates based on the root cause and affected parties.

Determine which communications are needed:
- **Management Briefing**: Always generated. Informs senior management of the root cause and action plan.
- **Supplier Communication**: Generated when the root cause involves a supplier or external vendor.
- **Internal Team Memo**: Generated when the root cause requires process changes that the team must follow.
- **Customer Communication**: Generated when customers were directly affected by the problem.

For each communication:
- Use the corresponding template from `references/communication-templates.md`.
- Replace all placeholders with specific, factual content from the investigation and action package.
- Match the tone to the audience (executive for management, professional-collaborative for suppliers, direct-supportive for team, empathetic-professional for customers).
- Include the root cause summary, financial impact, immediate actions taken, preventive measures planned, and monitoring approach.
- Keep communications concise — lead with the bottom line, then provide supporting detail.
- Subject lines must include an urgency indicator (URGENT, HIGH, MEDIUM) matching the highest action priority.

Present each communication draft as a complete, ready-to-send message (subject line + body). The user should be able to copy and send without further editing.

## Traceability Verification

Before presenting the final output, verify root cause traceability across the entire package:

1. List all elements of the validated root cause.
2. For each element, confirm at least one action addresses it.
3. List all actions in the package.
4. For each action, confirm it traces to a specific root cause element.
5. If any root cause element has no corresponding action, add one.
6. If any action has no root cause trace, remove it or reframe it.

State the traceability verification result explicitly: "All [N] root cause elements are addressed by [M] actions. No orphan actions detected."

## Output Package

Present the complete action package to the user, containing all five components in order:

1. **Immediate Actions** — Numbered list with full detail per action.
2. **Preventive Actions** — Numbered list with full detail per action.
3. **Monitoring Controls** — KPI table with thresholds and escalation paths.
4. **Action Register** — Consolidated table sorted by priority and deadline.
5. **Communication Drafts** — Ready-to-send messages for each relevant audience.

Include the traceability verification statement at the end of the package.

## Key Principles

- **Root Cause Traceability**: Every action traces directly to the validated root cause. This is the inviolable rule of this skill.
- **SME Realism**: Actions must be realistic for SME resources. Do not propose enterprise-scale solutions, large technology investments, or processes that require dedicated full-time roles the SME likely does not have.
- **Actionability**: Every action must be specific enough that the assigned owner can execute it without further interpretation. "Improve inventory management" is not actionable; "Implement a daily stockout check at 9:00 AM by the warehouse supervisor, with escalation to the operations manager if any SKU is below safety stock" is actionable.
- **Completeness**: The package must be self-contained — a manager should be able to act on it without needing additional information or analysis.
- **Communication Readiness**: Drafts must be ready to send. The user should not need to write or restructure them — only review and approve.

## Bundled References

| Reference File | Load At | Content |
|----------------|---------|---------|
| `references/action-design-framework.md` | Steps 1-2 | Action quality criteria, priority levels, deadline guidelines, success metric design, completeness checklist. |
| `references/communication-templates.md` | Step 5 | Email and memo templates for management, supplier, team, and customer communications, with customization rules. |
