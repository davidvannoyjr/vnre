# Ideas Vault

Cross-device idea capture for DVN. Any idea dropped in a Claude Code or Cowork session gets
logged to `ideas.json`, the HTML master doc is rebuilt, and a push to GitHub makes it available
on every device immediately.

## Files

| File | Purpose |
|------|---------|
| `ideas.json` | Source of truth — all captured ideas |
| `scripts/capture_idea.py` | Capture + HTML rebuild script |
| `SKILL.md` | Claude skill definition (triggers, process, output) |
| `../../ideas-master.html` | Human-readable master doc (repo root) |

## Quick start

```bash
# Capture an idea
python3 tools/shared/ideas-vault/scripts/capture_idea.py \
  --text "Your idea here" \
  --category VNRE \
  --priority High

# Update an idea's status
python3 tools/shared/ideas-vault/scripts/capture_idea.py \
  --update IDEA-003 --status Shipped

# Rebuild the HTML only (no new idea)
python3 tools/shared/ideas-vault/scripts/capture_idea.py --rebuild-html

# Self-test
python3 tools/shared/ideas-vault/scripts/capture_idea.py --selftest
```

## Idea structure

```json
{
  "id":       "IDEA-001",
  "date":     "2026-06-26",
  "text":     "The idea",
  "category": "VNRE",
  "priority": "High",
  "status":   "New",
  "project":  "optional-skill-name",
  "tags":     ["tag1", "tag2"],
  "source":   "code"
}
```

**Categories:** VNRE · Coaching · AI-Tech · Marketing · Operations · Product · Other  
**Priorities:** High · Normal · Low  
**Statuses:** New · In Progress · Shipped · Parked  
**Sources:** code (Claude Code session) · cowork (Cowork task)

## Multi-device sync

Ideas land on all devices the moment you push. Pull before a new session:

```bash
git pull origin <branch>
```

The HTML master doc (`ideas-master.html`) at the repo root opens in any browser — no tooling
required.
