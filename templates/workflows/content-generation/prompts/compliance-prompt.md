# Compliance Guide Generation Instructions

You are generating compliance control implementation guides for UK organisations.

## Article Structure

```markdown
---
title: "{Framework} {Control ID}: {Control Name} | Compliance Guide"
description: "How to implement {Framework} {Control ID} ({Control Name}). Practical guidance for UK organisations."
slug: "compliance/{framework-slug}/{control-id-slug}"
type: "compliance"
framework: "{Framework}"
control_id: "{Control ID}"
control_name: "{Control Name}"
domain: "{Domain/Category}"
date: {YYYY-MM-DD}
---

# {Framework} {Control ID}: {Control Name}

## What This Control Requires

{Plain English explanation of what the control mandates:
- The actual requirement (paraphrase, don't copy verbatim)
- Scope - what systems/processes it applies to
- Any specific thresholds or criteria}

## Why It Matters

{Risk context:
- What could go wrong without this control
- Real-world examples of failures (WebSearch if needed)
- Business impact of non-compliance
- How auditors assess this control}

## Implementation Guidance

### Step 1: {First Action}

{Specific, actionable guidance:
- What to do
- Who should be involved
- Tools or technologies that help
- Example configurations if applicable}

### Step 2: {Second Action}

{Continue with concrete steps...}

### Step 3: {Third Action}

{...}

## Evidence Required

Auditors and assessors will look for:

- {Specific document or artifact}
- {Policy or procedure}
- {Technical configuration or log}
- {Training record or acknowledgment}

## Common Pitfalls

- **{Pitfall 1}**: {What goes wrong and how to avoid it}
- **{Pitfall 2}**: {What goes wrong and how to avoid it}
- **{Pitfall 3}**: {What goes wrong and how to avoid it}

## NCSC Guidance

{Reference relevant NCSC guidance if applicable:
- Link to specific NCSC resource
- How it relates to this control
- Additional UK-specific considerations}

## How Wexley Labs Helps

We help organisations implement {Framework} through:

- **Gap assessments**: Identify where you stand against {Framework} requirements
- **Policy development**: Create documentation that satisfies auditors
- **Technical implementation**: Configure systems to meet control requirements
- **Audit preparation**: Ready your evidence and team for assessment

[Get a {Framework} Gap Assessment](/contact/)

## Related Controls

- [{Control ID 1}: {Name}](/compliance/{framework}/{control-1}/) - {Brief relation}
- [{Control ID 2}: {Name}](/compliance/{framework}/{control-2}/) - {Brief relation}
- [{Control ID 3}: {Name}](/compliance/{framework}/{control-3}/) - {Brief relation}
```

## Content Rules

1. **Length**: 500-800 words
2. **Language**: British English
3. **Accuracy**: WebSearch to verify control requirements if unsure
4. **Specificity**: Actionable steps, not vague guidance
5. **Evidence focus**: Always specify what auditors look for
6. **UK context**: Reference NCSC, ICO, or relevant UK body where applicable

## Frameworks to Cover

| Framework | Controls | Notes |
|-----------|----------|-------|
| ISO 27001:2022 | Annex A (93 controls) | Use 2022 version |
| NIST CSF 2.0 | ~100 subcategories | Updated 2024 |
| Cyber Essentials | 5 technical controls | UK government scheme |
| PCI DSS 4.0 | 12 requirements | Payment card |
| SOC 2 | Trust Service Criteria | Service organisations |

## What to Avoid

- Copying control text verbatim (paraphrase)
- Generic advice: "implement appropriate controls"
- Missing evidence requirements
- Ignoring UK-specific guidance (NCSC, ICO)
- Forgetting to link related controls
