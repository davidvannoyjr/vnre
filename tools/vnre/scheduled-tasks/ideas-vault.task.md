# Scheduled Task — ideas-vault weekly digest

- **Name:** `ideas-vault-weekly`
- **Schedule:** Weekly — **Monday 7:15 AM**
- **Skill:** `ideas-vault`
- **Output:** rebuilt `ideas-master.html` pushed to GitHub + inline digest in chat

## Trigger prompt (paste verbatim)

```
Run the weekly Ideas Vault digest.

1. Read tools/shared/ideas-vault/ideas.json.

2. Rebuild the HTML master doc:
   python3 tools/shared/ideas-vault/scripts/capture_idea.py \
     --rebuild-html \
     --data tools/shared/ideas-vault/ideas.json \
     --html ideas-master.html

3. Commit and push the rebuilt HTML:
   git add tools/shared/ideas-vault/ideas.json ideas-master.html
   git commit -m "vault: weekly digest rebuild $(date +%Y-%m-%d)" --allow-empty
   git push -u origin main

4. Print a digest in this format — no commentary, no preamble, just the table:

IDEAS VAULT — weekly digest <today's date>
Total: N  |  New: N  |  In Progress: N  |  Shipped: N  |  Parked: N

NEEDS REVIEW (New or In Progress > 14 days old):
  IDEA-NNN  [Category · Priority]  <date>  "<first 60 chars of text>"

IN PROGRESS:
  IDEA-NNN  [Category]  <date>  "<first 60 chars of text>"

NEW (last 7 days):
  IDEA-NNN  [Category · Priority]  <date>  "<first 60 chars of text>"

PARKED:
  IDEA-NNN  [Category]  <date>  "<first 60 chars of text>"

If a section is empty, omit it. If vault is empty, print: "Vault is empty — nothing to review."
```

## On failure
- `ideas.json` missing → recreate with `[]`, rebuild HTML, push.
- Git push fails → retry up to 3 times with 5s backoff; if still failing, print the digest in chat and note "HTML push failed — retry manually."
- Script error → print the raw JSON digest from ideas.json directly in chat.

## Notes
- This is a read + rebuild + push only. It never deletes, edits, or reorders ideas.
- The push target is whatever branch is currently checked out in the session.
- HTML rebuild is idempotent — safe to run at any time outside the schedule.
