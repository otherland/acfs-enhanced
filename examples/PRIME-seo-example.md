# Beads Workflow Context - Wexley Labs SEO Generation

> **Context Recovery**: This is auto-injected on SessionStart and PreCompact

## 🎯 YOUR MISSION: SEO Content Generation

You are generating cybersecurity glossary articles for Wexley Labs (UK penetration testing consultancy).

## WORKFLOW (Follow Exactly)

```bash
# 0. HEARTBEAT: Identify yourself (run once at start)
# Replace AGENT_NAME with your pane title (e.g., seo-test__cc_1)
export AGENT_NAME="seo-agent-1"
export SESSION_NAME="seo-test"
export PANE_NUM="2"
export ARTICLES_DONE=0

# 1. FIRST: Get procedural rules from CASS Memory
cm context "generate glossary article" --json

# 2. Find ready SEO work
bd ready --label=seo --label=glossary --json

# 3. Claim ONE bead ATOMICALLY (fails fast if already claimed by another agent)
bd update <bead-id> --claim
# If claim fails, pick a DIFFERENT bead from the ready list and retry
seo/scripts/heartbeat.sh "$AGENT_NAME" "$SESSION_NAME" "$PANE_NUM" "<bead-id>" "$ARTICLES_DONE"

# 4. Get the bead details (has slug, category)
bd show <bead-id>

# 5. Read format instructions
# - seo/prompts/glossary-prompt.md (article structure)
# - seo/context/brand-voice.md (tone, British English)

# 6. Research with WebSearch (2023-2024 examples)

# 7. Write article to: seo/output/glossary/{slug}.md

# 8. Close the bead and update heartbeat
bd close <bead-id> --reason="Generated {slug}.md"
ARTICLES_DONE=$((ARTICLES_DONE + 1))
seo/scripts/heartbeat.sh "$AGENT_NAME" "$SESSION_NAME" "$PANE_NUM" "null" "$ARTICLES_DONE"

# 9. LOOP: Go back to step 2 until no more ready beads
```

## HEARTBEAT (Important for Monitoring)

Send heartbeats so the monitor knows you're alive:
```bash
# When claiming a bead:
seo/scripts/heartbeat.sh "agent-name" "session" "pane" "bead-id" "articles_completed"

# When idle/between beads:
seo/scripts/heartbeat.sh "agent-name" "session" "pane" "null" "articles_completed"
```

The monitor checks `.heartbeats/` directory. If no heartbeat for 5 minutes, you're considered stuck.

## KEY RULES

- **British English**: organisation, defence, colour, prioritise
- **400-600 words** per article
- **WebSearch required** for current breach examples
- **Avoid AI patterns**: "Additionally", "Furthermore", "It's important to note"
- **One bead at a time**: Claim → Complete → Next

## ARTICLE FORMAT

```markdown
---
title: "What is {Term}? | Cybersecurity Glossary"
description: "{One sentence, under 155 chars}"
slug: "{slug}"
type: "glossary"
category: "{attack|defence|concept|framework|tool}"
date: YYYY-MM-DD
lastmod: YYYY-MM-DD
---

# What is {Term}?

**{Term}** is {2-3 sentence definition}.

## How {Term} Works
{Technical explanation, 2-3 paragraphs}

## Real-World Examples
{1-2 specific incidents with dates}

## How to Defend Against {Term} / How to Implement {Term}
{Actionable guidance}

## Related Terms
- [Term 1](/glossary/slug-1/)
- [Term 2](/glossary/slug-2/)

## Need Help?
If you're concerned about {term}, [contact our team](/contact/) for a security assessment.
```

## FEEDBACK (During Work)

When a rule from cm context helps:
```javascript
// [cass: helpful b-xxx] - this pattern worked well
```

When a rule causes problems:
```javascript
// [cass: harmful b-xxx] - this caused issues because...
```

## SESSION CLOSE PROTOCOL

When no more beads are ready:
```bash
bd sync
git add seo/output/
git commit -m "Generated glossary articles: {list slugs}"
git push
```

Report: "COMPLETE - Generated N articles: {list slugs}"
