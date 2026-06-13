#!/usr/bin/env python3
"""
audit_file.py — VNRE Stage 06 transaction-file compliance auditor.

Checks a transaction folder against a required-documents checklist per stage
(listing / under-contract / closing): which required docs are present, which are
missing, which are present-but-need-signature-verification, plus deadline flags.

NOT legal certification. It's a completeness aid — a licensed broker must review and
sign off. It checks document presence + naming and flags signature docs for human
verification; it does not validate e-signature legal sufficiency.

Architecture (mirrors the other skills): Claude lists the Drive transaction folder
(Drive MCP) → this deterministic script evaluates the checklist → report. No network.
"""
import argparse
import json
import re
from datetime import date, datetime


def parse_date(s):
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def match_present(spec, files):
    """A required doc is present if any of its match patterns hits any filename."""
    for pat in spec.get("match", []):
        rx = re.compile(pat, re.I)
        for f in files:
            if rx.search(f):
                return f
    return None


def applicable(spec, ctx):
    """Conditional docs (e.g. lead paint only pre-1978)."""
    cond = spec.get("conditional")
    if not cond:
        return True
    if cond == "pre1978":
        yb = ctx.get("yearBuilt")
        return not (isinstance(yb, int) and yb >= 1978)
    return True  # unknown condition → keep it (safer to require)


def audit(checklist, stage, files, ctx, today):
    stages = checklist["stages"]
    if stage not in stages:
        raise ValueError(f"unknown stage '{stage}'. Known: {', '.join(stages)}")
    sdef = stages[stage]
    missing, verify, complete, na, matched_files = [], [], [], [], set()

    for spec in sdef["required"]:
        if not applicable(spec, ctx):
            na.append(spec["name"])
            continue
        hit = match_present(spec, files)
        if hit:
            matched_files.add(hit)
            (verify if spec.get("signature") else complete).append({"name": spec["name"], "file": hit})
        else:
            missing.append({"name": spec["name"], "signature": bool(spec.get("signature"))})

    other = [f for f in files if f not in matched_files]

    # deadlines
    deadlines = []
    for key in checklist.get("dateChecks", []):
        d = parse_date((ctx.get("dates") or {}).get(key))
        if not d:
            continue
        days = (d - today).days
        if days < 0:
            deadlines.append((key, d, days, "OVERDUE"))
        elif days <= 3:
            deadlines.append((key, d, days, "DUE SOON"))
        else:
            deadlines.append((key, d, days, "ok"))

    return {"stage": stage, "label": sdef.get("label", stage), "missing": missing,
            "verify": verify, "complete": complete, "na": na, "other": other,
            "deadlines": deadlines}


def render(r, today):
    ready = not r["missing"]
    L = [f"# Compliance Check — {r['label']}  ({today.isoformat()})", "",
         (f"✅ **All required documents present.** {len(r['verify'])} need signature "
          f"verification before close." if ready else
          f"🔴 **{len(r['missing'])} required document(s) missing.** Not ready for broker sign-off."),
         "", "> Completeness aid only — a licensed broker must review and approve. Signature items "
         "are flagged for human verification; this does not certify e-signature validity.", ""]
    if r["missing"]:
        L += ["## 🔴 Missing — required", ""]
        L += [f"- **{m['name']}**" + (" *(needs signatures)*" if m["signature"] else "") for m in r["missing"]]
        L.append("")
    if r["verify"]:
        L += ["## ⚠️ Present — verify all signatures/initials/dates", ""]
        L += [f"- {v['name']}  ·  `{v['file']}`" for v in r["verify"]]
        L.append("")
    if r["complete"]:
        L += ["## ✅ Present", ""]
        L += [f"- {c['name']}  ·  `{c['file']}`" for c in r["complete"]]
        L.append("")
    if r["na"]:
        L += ["## ➖ Not applicable", "", ", ".join(r["na"]), ""]
    if r["deadlines"]:
        L += ["## ⏰ Deadlines", "", "| Item | Date | Days | Status |", "|---|---|---:|---|"]
        flag = {"OVERDUE": "🔴", "DUE SOON": "🟡", "ok": "🟢"}
        for k, d, days, st in r["deadlines"]:
            L.append(f"| {k} | {d.isoformat()} | {days} | {flag[st]} {st} |")
        L.append("")
    if r["other"]:
        L += ["## 📎 Other files in folder (not matched to a required doc)", "",
              ", ".join(f"`{f}`" for f in r["other"]), ""]
    return "\n".join(L).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", help="JSON list of filenames in the transaction folder")
    ap.add_argument("--checklist", help="checklist JSON")
    ap.add_argument("--stage", help="listing | under_contract | closing")
    ap.add_argument("--context", help="optional JSON {yearBuilt, dates:{...}}")
    ap.add_argument("--out")
    ap.add_argument("--today", default=date.today().isoformat())
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not (args.manifest and args.checklist and args.stage):
        ap.error("--manifest, --checklist and --stage required (or --selftest)")

    files = json.load(open(args.manifest))
    files = files.get("files", files) if isinstance(files, dict) else files
    checklist = json.load(open(args.checklist))
    ctx = json.load(open(args.context)) if args.context else {}
    r = audit(checklist, args.stage, files, ctx, parse_date(args.today))
    md = render(r, parse_date(args.today))
    (open(args.out, "w").write(md) if args.out else print(md))
    print(f"audit: {len(r['missing'])} missing, {len(r['verify'])} to verify, "
          f"{len(r['complete'])} complete -> {args.out or 'stdout'}")


def selftest():
    checklist = {
        "stages": {"listing": {"label": "Listing signed", "required": [
            {"name": "ERS Listing Agreement", "match": ["ers", "exclusive right", "listing agreement"], "signature": True},
            {"name": "Seller's Disclosure", "match": [r"seller.*disclosure", "condition of property"], "signature": True},
            {"name": "Lead-Based Paint", "match": ["lead", "lbp"], "signature": True, "conditional": "pre1978"},
            {"name": "Wire Fraud Advisory", "match": ["wire fraud"], "signature": False},
        ]}},
        "dateChecks": ["closingDate"],
    }
    files = ["2026 ERS Exclusive Right to Sell - signed.pdf",
             "Sellers Disclosure and Condition of Property.pdf",
             "random scan.pdf"]
    # newer home (2015) → lead paint N/A; wire fraud advisory missing
    ctx = {"yearBuilt": 2015, "dates": {"closingDate": "2026-06-15"}}
    r = audit(checklist, "listing", files, ctx, date(2026, 6, 13))
    assert [m["name"] for m in r["missing"]] == ["Wire Fraud Advisory"], r["missing"]
    assert {v["name"] for v in r["verify"]} == {"ERS Listing Agreement", "Seller's Disclosure"}, r["verify"]
    assert r["na"] == ["Lead-Based Paint"], r["na"]            # 2015 build
    assert "random scan.pdf" in r["other"]
    assert r["deadlines"][0][3] == "DUE SOON"                  # closing in 2 days
    # pre-1978 home → lead paint becomes required (and missing)
    r2 = audit(checklist, "listing", files, {"yearBuilt": 1956}, date(2026, 6, 13))
    assert any(m["name"] == "Lead-Based Paint" for m in r2["missing"])
    print("selftest OK — presence/missing, signature-verify, pre-1978 conditional, deadlines, other-files all correct")


if __name__ == "__main__":
    main()
