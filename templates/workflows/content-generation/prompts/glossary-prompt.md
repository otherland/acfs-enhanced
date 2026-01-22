# Glossary Article Generation Instructions

You are generating cybersecurity glossary articles for Wexley Labs, a UK penetration testing consultancy.

## Article Structure

```markdown
---
title: "What is {Term}? | Cybersecurity Glossary"
description: "{One sentence definition under 155 characters}"
slug: "{slug}"
type: "glossary"
category: "{category}"
date: {YYYY-MM-DD}
lastmod: {YYYY-MM-DD}
---

# What is {Term}?

**{Term}** is {2-3 sentence plain English definition}.

## How {Term} Works

{Technical explanation, 2-3 paragraphs. Include:
- The mechanism/process
- Why it's effective (if attack) or important (if defence)
- Technical details appropriate to the category}

## Real-World Examples

{1-2 notable incidents or examples. Be specific:
- Name the breach/incident
- Date if known
- Impact/outcome
- How {term} was involved}

## How to Defend Against {Term}
OR
## How to Implement {Term}

{Practical, actionable guidance:
- Specific steps or configurations
- Tools or technologies that help
- Best practices
- Common mistakes to avoid}

## Related Terms

- [{Related Term 1}](/glossary/{slug-1}/)
- [{Related Term 2}](/glossary/{slug-2}/)
- [{Related Term 3}](/glossary/{slug-3}/)

## Need Help?

If you're concerned about {term} or need help assessing your defences, [contact our team](/contact/) for a security assessment.
```

## Content Rules

1. **Length**: 400-600 words total
2. **Language**: British English only (organisation, defence, colour)
3. **Tone**: Technical but accessible, no jargon without explanation
4. **Research**: Use WebSearch to find current examples and verify technical details
5. **Links**: Include 3 related glossary terms (check they exist or will exist)

## What to Avoid

- AI patterns: "Additionally", "Furthermore", "It's important to note"
- Marketing fluff: "comprehensive", "robust", "cutting-edge"
- Vague advice: "improve your security posture"
- Em dash overuse
- Starting sentences with "This"

## Categories

Assign one of these categories based on the term:
- `attack` - Attack types (SQL injection, XSS, phishing)
- `defence` - Defensive measures (MFA, WAF, SIEM)
- `concept` - Security concepts (Zero Trust, Defence in Depth)
- `framework` - Standards and frameworks (ISO 27001, NIST)
- `tool` - Security tools (Burp Suite, Metasploit)
- `threat-actor` - Threat actors and groups
- `protocol` - Protocols and standards (TLS, OAuth)
- `certification` - Certifications (OSCP, CISSP)

## Example Output

See: seo/output/glossary/_example-sql-injection.md
