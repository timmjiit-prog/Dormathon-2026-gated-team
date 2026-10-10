# Specialist Roles & Delegation Guide

This reference defines the specialist roles that RootIQ Orchestrator delegates to during the investigation, including their scope, key analysis areas, and delegation prompts.

## Overview

RootIQ Orchestrator delegates factual data findings to specialist agents for domain-specific interpretation. Each specialist receives the relevant data analysis results and returns domain insights, preliminary root cause hypotheses, and recommended focus areas.

## Specialist Roles

### 1. Sales Specialist

**Scope**: Revenue, pricing, sales channels, product performance, and sales team effectiveness.

**Key Analysis Areas**:
- Revenue trend analysis (by product, channel, region, customer segment)
- Pricing impact (price changes, discounts, promotions)
- Sales volume vs. average order value decomposition
- Channel performance comparison
- Product mix and portfolio changes
- Sales pipeline and conversion rate changes
- Seasonality and cyclical pattern assessment

**Delegation Focus**: Given the data findings, identify which sales-related factors contributed to the observed problem, quantify their impact, and propose hypotheses about the sales-side root causes.

### 2. Inventory & Procurement Specialist

**Scope**: Stock management, supply chain operations, supplier performance, procurement processes, and inventory efficiency.

**Key Analysis Areas**:
- Inventory turnover and days of supply
- Stockout frequency and duration by SKU
- Supplier delivery performance (on-time rate, lead time changes)
- Procurement order accuracy and completeness
- Carrying cost analysis
- Supply chain disruption indicators
- Safety stock adequacy assessment
- Supplier concentration risk

**Delegation Focus**: Given the data findings, identify supply-side factors that contributed to the observed problem, quantify stockout or oversupply impact, and propose hypotheses about procurement and inventory root causes.

### 3. Customer & Operations Specialist

**Scope**: Customer behavior, retention, satisfaction signals, operational processes, service quality, and fulfillment.

**Key Analysis Areas**:
- Customer retention and churn rates
- New customer acquisition trends
- Order fulfillment cycle time
- Return/refund rates and reasons
- Customer complaint patterns
- Service level agreement (SLA) compliance
- Operational bottleneck identification
- Customer lifetime value changes
- Repeat purchase behavior

**Delegation Focus**: Given the data findings, identify customer-side and operational factors that contributed to the observed problem, quantify behavioral or process impact, and propose hypotheses about customer and operational root causes.

## Delegation Protocol

### When to Delegate

Delegate after Step 3 (Execute Data Analysis) has produced factual findings. Specialists receive the data analysis results — they do not re-analyze raw data.

### What to Send Each Specialist

Provide each specialist with:
1. **Business Context**: The observed problem, affected metrics, and investigation period.
2. **Relevant Data Findings**: The specific analytical results within their domain (tables, metrics, trends).
3. **Task**: Analyze the findings, identify contributing factors, quantify impact, and propose hypotheses.

### What to Expect Back

Each specialist should return:
1. **Key Findings**: 3-5 significant factual discoveries within their domain.
2. **Quantified Impact**: Dollar amounts or percentages for each finding's contribution.
3. **Preliminary Hypotheses**: 1-2 domain-specific root cause hypotheses.
4. **Cross-Domain Signals**: Any patterns that may connect to another specialist's domain.

### Integration Rules

- Collect all specialist findings before forming hypotheses.
- Look for convergence: when multiple specialists independently point to the same underlying cause, confidence increases.
- Look for divergence: when specialists' findings conflict, flag the discrepancy for evidence validation.
- Specialist hypotheses feed into Step 5 (Generate Hypotheses) but do not replace the orchestrator's independent evaluation.
