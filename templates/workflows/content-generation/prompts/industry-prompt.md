# Industry Page Generation Instructions

You are generating industry-specific service pages for Wexley Labs, targeting UK sectors.

## Article Structure

```markdown
---
title: "{Service} for {Industry} | Wexley Labs"
description: "{Service} tailored for UK {industry} organisations. Meet {primary regulation} requirements. CREST-certified."
slug: "{service-slug}-{industry-slug}"
type: "industry"
service: "{service}"
industry: "{industry}"
regulations: ["{reg1}", "{reg2}"]
date: {YYYY-MM-DD}
---

# {Service} for {Industry}

{Opening paragraph - why {industry} is a target and needs {service}. Include:
- Recent breach statistics for sector (WebSearch for current data)
- Why attackers target this industry
- Stakes involved (data types, operational impact)}

## Why {Industry} is Targeted

{2-3 paragraphs covering:
- Valuable data/assets in this sector
- Common attack vectors used against {industry}
- Recent notable breaches (WebSearch for examples)
- Threat actor interest in this sector}

## Regulatory Requirements for {Industry}

{CRITICAL SECTION - must be specific to UK:
- List specific regulations from data file
- What each requires regarding security testing
- Compliance deadlines or audit cycles
- Penalties for non-compliance}

**Key regulations:**
{For each regulation in the data:}
- **{Regulation}**: {What it requires, how {service} helps meet it}

## Common Vulnerabilities We Find in {Industry}

{Based on industry characteristics:
- Sector-specific systems (e.g., SCADA for energy, HL7 for healthcare)
- Legacy system issues common in sector
- Third-party/supply chain risks
- Human factors specific to sector}

## Our {Service} Methodology for {Industry}

{How we adapt our approach:
- Understanding of sector-specific systems
- Compliance-aware testing
- Minimal operational disruption
- Sector experience}

## Deliverables

- {Industry}-focused assessment report
- Compliance mapping to {primary regulation}
- Executive summary for board/regulator reporting
- Technical findings with remediation guidance
- Risk-rated vulnerability list
- Follow-up support

## Get Started

Protect your {industry} organisation with security testing that understands your sector.

**Call us**: +44 208 058 4503
**Email**: hello@wexleylabs.com

[Book a Consultation](/contact/)
```

## Content Rules

1. **Length**: 600-900 words
2. **Language**: British English
3. **Research**: WebSearch for:
   - "{industry} UK cyber breach 2024" for recent incidents
   - "{industry} {regulation} requirements" for compliance details
4. **Regulations**: MUST include specific UK regulations from data file
5. **Specificity**: Reference sector-specific technologies and systems

## Industry-Regulation Mapping (from data)

| Industry | Key Regulations |
|----------|-----------------|
| Healthcare/NHS | NHS DSPT, GDPR, NIS2 |
| Financial Services | FCA, PRA, GDPR, DORA |
| Legal | SRA, GDPR, Cyber Essentials |
| Government | GovAssure, Cyber Essentials Plus |
| Energy | NIS2, CAF |
| Retail | PCI DSS, GDPR |

## What to Avoid

- Generic security advice not specific to the industry
- Missing or vague regulatory references
- Outdated breach examples (WebSearch for recent ones)
- Ignoring sector-specific systems and technologies
