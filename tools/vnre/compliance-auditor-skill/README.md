# vnre-compliance-auditor — Stage 06 (Compliance)

Audits a transaction folder against a per-stage required-documents checklist: flags **missing**
docs, docs that **need signature verification**, and **deadline** risk. A completeness aid for
broker review — not legal certification.

## Files
```
compliance-auditor-skill/
├── SKILL.md, README.md
├── checklist.example.json     # required docs per stage (copy -> checklist.json, confirm with broker)
├── scripts/audit_file.py
└── sample/  (sample_manifest.json, sample_context.json)
```

## Try it (no network)
```bash
python3 scripts/audit_file.py --selftest
python3 scripts/audit_file.py \
  --manifest sample/sample_manifest.json --checklist checklist.example.json \
  --stage listing --context sample/sample_context.json --out /tmp/audit.md --today 2026-06-13
cat /tmp/audit.md
```

## How it works
- **Manifest** = the filenames in the Drive transaction folder (Claude lists it via the Drive MCP).
- **Checklist** = required docs per stage with regex `match` patterns, a `signature` flag, and
  optional `conditional` (`pre1978` → lead-paint only for older homes).
- **Context** = `yearBuilt` (conditionals) + `dates` (deadline flags).
- Output groups every required doc as 🔴 missing / ⚠️ verify-signatures / ✅ present / ➖ N/A, plus
  a deadline table and any unmatched "other files".

## Important
This checks **presence + naming**, not e-signature legal validity. **A licensed broker must
review and sign off.** Tune the audit by editing `checklist.json` — confirm the form set with
your broker / Heartland MLS.
