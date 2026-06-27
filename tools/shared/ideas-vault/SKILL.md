---
name: ideas-vault
description: Capture a business, tech, or workflow idea to the cross-device vault — log it to ideas.json, rebuild the HTML master doc (ideas-master.html), and push to GitHub so it lands on every device instantly. Use whenever DVN says "capture this idea", "log an idea", "new idea:", "add to the vault", or drops any thought worth preserving mid-session. Also handles status updates: "mark IDEA-007 as shipped", "park IDEA-003". Covers VNRE ops, DVN Coaching, AI/Tech, Marketing, Operations, and Product ideas.
---

# Ideas Vault — cross-device idea capture

Captures any idea DVN drops in-session, stores it to the version-controlled vault, and pushes to
GitHub. `ideas-master.html` at the repo root is the human-readable view — open in any browser,
zero setup, works on every device.

## Triggers
- "capture this idea: …"
- "log an idea: …" / "new idea: …"
- "add to the vault: …"
- "mark IDEA-NNN as shipped / in progress / parked"
- any spontaneous thought DVN wants to preserve mid-session

## What to extract
From DVN's message, determine:

| Field       | Values                                                    | Default   |
|-------------|-----------------------------------------------------------|-----------|
| `text`      | the idea itself (clean phrasing, preserve intent)         | required  |
| `category`  | VNRE · Coaching · AI-Tech · Marketing · Operations · Product · Other | infer from context |
| `priority`  | High · Normal · Low                                       | Normal    |
| `project`   | active project/skill name if obvious (e.g. "active-hunter-skill") | ""  |
| `tags`      | 1–3 lowercase keywords                                    | ""        |
| `source`    | code · cowork                                             | code      |

**Category inference guide:**
- VNRE → brokerage operations, listings, FUB, prospecting, transactions
- Coaching → DVN Coaching product, clients, 22-Point System, curriculum
- AI-Tech → aiDrVN model, MCP tools, automations, Claude skills
- Marketing → content, social, brand, email campaigns
- Operations → SOPs, team workflows, systems, admin
- Product → something to build and sell; sellable aiDrVN components

## Process — new idea

```bash
python3 tools/shared/ideas-vault/scripts/capture_idea.py \
  --text "Exact idea text here" \
  --category VNRE \
  --priority Normal \
  --project "optional-project-name" \
  --tags "tag1,tag2" \
  --source code \
  --data tools/shared/ideas-vault/ideas.json \
  --html ideas-master.html
```

Then commit and push:

```bash
git add tools/shared/ideas-vault/ideas.json ideas-master.html
git commit -m "vault: IDEA-NNN — <3-5 word summary>"
git push -u origin <current-branch>
```

## Process — status update

```bash
python3 tools/shared/ideas-vault/scripts/capture_idea.py \
  --update IDEA-007 \
  --status Shipped \
  --data tools/shared/ideas-vault/ideas.json \
  --html ideas-master.html

git add tools/shared/ideas-vault/ideas.json ideas-master.html
git commit -m "vault: IDEA-007 → Shipped"
git push -u origin <current-branch>
```

Valid statuses: **New · In Progress · Shipped · Parked**

## Output
One-line confirm: `IDEA-NNN captured (Category · Priority) — synced to all devices.`
No summary, no recap, no explanation unless DVN asks.

## Verify offline
```bash
python3 tools/shared/ideas-vault/scripts/capture_idea.py --selftest
```
