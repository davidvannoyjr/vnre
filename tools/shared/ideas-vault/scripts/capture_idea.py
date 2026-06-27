#!/usr/bin/env python3
"""
Ideas Vault — capture_idea.py

Append an idea to ideas.json, then rebuild ideas-master.html.

Usage:
  # Capture a new idea
  python3 capture_idea.py \
    --text "Your idea here" \
    --category VNRE \
    [--priority High|Normal|Low] \
    [--project "project name"] \
    [--tags "tag1,tag2"] \
    [--source code|cowork] \
    [--data PATH/ideas.json] \
    [--html PATH/ideas-master.html]

  # Update an existing idea's status
  python3 capture_idea.py --update IDEA-003 --status "In Progress"
  python3 capture_idea.py --update IDEA-007 --status Shipped

  # Rebuild HTML only (no new idea)
  python3 capture_idea.py --rebuild-html [--data PATH] [--html PATH]

  # Self-test
  python3 capture_idea.py --selftest
"""

import argparse
import json
import sys
import tempfile
from datetime import date
from pathlib import Path

# ── path defaults ─────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_VAULT_DIR  = _SCRIPT_DIR.parent
_REPO_ROOT  = _VAULT_DIR.parent.parent.parent

DEFAULT_DATA = _VAULT_DIR / "ideas.json"
DEFAULT_HTML = _REPO_ROOT / "ideas-master.html"

# ── constants ─────────────────────────────────────────────────────────────────
CATEGORIES = ["VNRE", "Coaching", "AI-Tech", "Marketing", "Operations", "Product", "Other"]
PRIORITIES = ["High", "Normal", "Low"]
STATUSES   = ["New", "In Progress", "Shipped", "Parked"]
SOURCES    = ["code", "cowork"]

CAT_COLORS = {
    "VNRE":       ["#C8102E", "#FFFFFF"],
    "Coaching":   ["#1e3c72", "#FFFFFF"],
    "AI-Tech":    ["#6f42c1", "#FFFFFF"],
    "Marketing":  ["#fd7e14", "#FFFFFF"],
    "Operations": ["#20c997", "#1C1C1C"],
    "Product":    ["#0dcaf0", "#1C1C1C"],
    "Other":      ["#adb5bd", "#1C1C1C"],
}
PRI_COLORS = {
    "High":   "#C8102E",
    "Normal": "#2a5298",
    "Low":    "#adb5bd",
}
STATUS_COLORS = {
    "New":         "#2a5298",
    "In Progress": "#e07b00",
    "Shipped":     "#198754",
    "Parked":      "#6E6E6E",
}

# ── data helpers ──────────────────────────────────────────────────────────────
def load(path: Path) -> list:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


def save(ideas: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(ideas, f, indent=2)
        f.write("\n")


def next_id(ideas: list) -> str:
    nums = []
    for idea in ideas:
        try:
            nums.append(int(idea["id"].split("-")[1]))
        except (KeyError, IndexError, ValueError):
            pass
    n = (max(nums) + 1) if nums else 1
    return f"IDEA-{n:03d}"


def make_idea(text: str, category: str, priority: str,
              project: str, tags: list, source: str, ideas: list) -> dict:
    return {
        "id":       next_id(ideas),
        "date":     date.today().isoformat(),
        "text":     text.strip(),
        "category": category,
        "priority": priority,
        "status":   "New",
        "project":  project.strip() if project else "",
        "tags":     [t.strip() for t in tags if t.strip()],
        "source":   source,
    }

# ── HTML generation ───────────────────────────────────────────────────────────
HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DVN Ideas Vault</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --red:#C8102E;--charcoal:#1C1C1C;--gray:#6E6E6E;
  --blue-dark:#1e3c72;--blue-mid:#2a5298;
  --bg:#f4f5f7;--surface:#fff;
  --radius:10px;--shadow:0 4px 18px rgba(0,0,0,.10);
}
body{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  font-size:14px;background:var(--bg);color:var(--charcoal);line-height:1.5
}
.header{
  background:linear-gradient(135deg,var(--blue-dark),var(--blue-mid));
  color:#fff;padding:32px 24px 24px;text-align:center
}
.header h1{font-size:26px;font-weight:700;letter-spacing:-.5px}
.header .sub{font-size:13px;opacity:.8;margin-top:6px}
.header .accent{color:#f4b8c1}
.controls{
  background:#fff;border-bottom:1px solid #e0e3e8;
  padding:14px 24px;position:sticky;top:0;z-index:10;
  display:flex;flex-wrap:wrap;gap:10px;align-items:center
}
#search{
  flex:1;min-width:180px;max-width:320px;
  padding:8px 14px;border:1.5px solid #d0d3d8;border-radius:6px;
  font-size:14px;outline:none;transition:border-color .2s
}
#search:focus{border-color:var(--blue-mid)}
.sep{width:1px;height:28px;background:#e0e3e8;flex-shrink:0}
.filters{display:flex;flex-wrap:wrap;gap:5px}
.status-filters{display:flex;flex-wrap:wrap;gap:5px}
.fbtn{
  padding:5px 12px;border:1.5px solid #d0d3d8;border-radius:20px;
  background:#fff;cursor:pointer;font-size:12px;font-weight:500;
  color:var(--gray);transition:all .15s;line-height:1.3
}
.fbtn:hover{background:#f0f2f5;border-color:#b0b3b8}
.fbtn.active{background:var(--blue-mid);border-color:var(--blue-mid);color:#fff}
.stats{
  display:flex;gap:20px;padding:10px 24px;background:#f8f9fb;
  border-bottom:1px solid #e8eaee;font-size:12px;color:var(--gray);flex-wrap:wrap
}
.stat-val{font-weight:700;color:var(--charcoal);margin-right:3px}
.grid{
  display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));
  gap:16px;padding:20px 24px
}
.card{
  background:var(--surface);border-radius:var(--radius);
  box-shadow:var(--shadow);padding:18px 20px;
  border-top:3px solid var(--blue-mid);
  display:flex;flex-direction:column;gap:10px;
  transition:transform .15s,box-shadow .15s
}
.card:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(0,0,0,.13)}
.card-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.card-id{font-size:11px;font-weight:600;color:var(--gray);letter-spacing:.3px;white-space:nowrap}
.badges{display:flex;gap:5px;flex-wrap:wrap;justify-content:flex-end}
.badge{
  font-size:10px;font-weight:700;padding:2px 8px;
  border-radius:20px;white-space:nowrap
}
.card-text{font-size:14px;font-weight:500;color:var(--charcoal);line-height:1.5}
.pdot{
  width:8px;height:8px;border-radius:50%;
  display:inline-block;margin-right:5px;vertical-align:middle
}
.card-meta{
  font-size:11px;color:var(--gray);
  display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-top:2px
}
.tag{background:#f0f2f5;padding:2px 7px;border-radius:4px;font-size:10px}
.proj{color:var(--blue-mid);font-weight:500}
.src{opacity:.6}
.empty{text-align:center;padding:60px 20px;color:var(--gray)}
.empty h3{font-size:18px;margin-bottom:8px}
@media(max-width:600px){
  .controls{flex-direction:column;align-items:stretch}
  #search{max-width:none}
  .grid{padding:12px;gap:12px}
}
</style>
</head>
<body>

<div class="header">
  <h1>DVN <span class="accent">Ideas Vault</span></h1>
  <div class="sub">Cross-device &middot; Version-controlled &middot; Built __GENERATED__</div>
</div>

<div class="controls">
  <input type="text" id="search" placeholder="Search ideas&hellip;" oninput="render()">
  <div class="sep"></div>
  <div class="filters">
    <button class="fbtn active" data-f="cat" data-v="all" onclick="setFilter(this,'cat')">All</button>
    <button class="fbtn" data-f="cat" data-v="VNRE" onclick="setFilter(this,'cat')">VNRE</button>
    <button class="fbtn" data-f="cat" data-v="Coaching" onclick="setFilter(this,'cat')">Coaching</button>
    <button class="fbtn" data-f="cat" data-v="AI-Tech" onclick="setFilter(this,'cat')">AI / Tech</button>
    <button class="fbtn" data-f="cat" data-v="Marketing" onclick="setFilter(this,'cat')">Marketing</button>
    <button class="fbtn" data-f="cat" data-v="Operations" onclick="setFilter(this,'cat')">Operations</button>
    <button class="fbtn" data-f="cat" data-v="Product" onclick="setFilter(this,'cat')">Product</button>
    <button class="fbtn" data-f="cat" data-v="Other" onclick="setFilter(this,'cat')">Other</button>
  </div>
  <div class="sep"></div>
  <div class="status-filters">
    <button class="fbtn active" data-f="st" data-v="all" onclick="setFilter(this,'st')">All Status</button>
    <button class="fbtn" data-f="st" data-v="New" onclick="setFilter(this,'st')">New</button>
    <button class="fbtn" data-f="st" data-v="In Progress" onclick="setFilter(this,'st')">In Progress</button>
    <button class="fbtn" data-f="st" data-v="Shipped" onclick="setFilter(this,'st')">Shipped</button>
    <button class="fbtn" data-f="st" data-v="Parked" onclick="setFilter(this,'st')">Parked</button>
  </div>
</div>

<div class="stats" id="stats"></div>
<div class="grid" id="grid"></div>

<script>
const IDEAS = __IDEAS_JSON__;
const CAT   = __CAT_COLORS_JSON__;
const PRI   = __PRI_COLORS_JSON__;
const STA   = __STATUS_COLORS_JSON__;

let filters = { cat: 'all', st: 'all' };

function setFilter(btn, dim) {
  document.querySelectorAll(`.fbtn[data-f="${dim}"]`).forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  filters[dim] = btn.dataset.v;
  render();
}

function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function badge(text, bg, color) {
  return `<span class="badge" style="background:${bg};color:${color}">${esc(text)}</span>`;
}

function render() {
  const q = document.getElementById('search').value.toLowerCase();
  const filtered = IDEAS.filter(i => {
    if (filters.cat !== 'all' && i.category !== filters.cat) return false;
    if (filters.st  !== 'all' && i.status   !== filters.st)  return false;
    if (!q) return true;
    return (
      i.text.toLowerCase().includes(q) ||
      i.id.toLowerCase().includes(q) ||
      (i.project||'').toLowerCase().includes(q) ||
      (i.tags||[]).some(t => t.toLowerCase().includes(q))
    );
  });

  // stats
  const counts = {};
  filtered.forEach(i => counts[i.status] = (counts[i.status]||0) + 1);
  document.getElementById('stats').innerHTML =
    `<span><span class="stat-val">${filtered.length}</span>ideas</span>` +
    Object.entries(counts).map(([s,c]) =>
      `<span><span class="stat-val" style="color:${STA[s]||'#333'}">${c}</span>${s}</span>`
    ).join('');

  const grid = document.getElementById('grid');
  if (!filtered.length) {
    grid.innerHTML = '<div class="empty"><h3>No ideas match</h3><p>Try a different search or filter.</p></div>';
    return;
  }
  const sorted = [...filtered].sort((a,b) => b.date.localeCompare(a.date) || b.id.localeCompare(a.id));
  grid.innerHTML = sorted.map(idea => {
    const [catBg, catFg] = CAT[idea.category] || ['#adb5bd','#1C1C1C'];
    const priColor  = PRI[idea.priority] || '#adb5bd';
    const staBg     = STA[idea.status]  || '#adb5bd';
    const tags = (idea.tags||[]).map(t => `<span class="tag">${esc(t)}</span>`).join('');
    const proj = idea.project ? `<span class="proj">${esc(idea.project)}</span>` : '';
    const src  = `<span class="src">${idea.source === 'cowork' ? 'Cowork' : 'Code'}</span>`;
    return `
<div class="card" style="border-top-color:${catBg}">
  <div class="card-top">
    <div class="card-id">${esc(idea.id)} &middot; ${esc(idea.date)}</div>
    <div class="badges">
      ${badge(idea.category, catBg, catFg)}
      ${badge(idea.status, staBg, '#fff')}
    </div>
  </div>
  <div class="card-text">
    <span class="pdot" style="background:${priColor}" title="Priority: ${esc(idea.priority)}"></span>${esc(idea.text)}
  </div>
  <div class="card-meta">${tags}${proj}${src}</div>
</div>`;
  }).join('');
}
render();
</script>
</body>
</html>
"""


def build_html(ideas: list, generated: str) -> str:
    return (
        HTML
        .replace("__GENERATED__",        generated)
        .replace("__IDEAS_JSON__",        json.dumps(ideas,        ensure_ascii=False))
        .replace("__CAT_COLORS_JSON__",   json.dumps(CAT_COLORS,   ensure_ascii=False))
        .replace("__PRI_COLORS_JSON__",   json.dumps(PRI_COLORS,   ensure_ascii=False))
        .replace("__STATUS_COLORS_JSON__", json.dumps(STATUS_COLORS, ensure_ascii=False))
    )


def write_html(ideas: list, html_path: Path) -> None:
    generated = date.today().isoformat()
    html_path.parent.mkdir(parents=True, exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html(ideas, generated))

# ── self-test ─────────────────────────────────────────────────────────────────
SELFTEST_IDEAS = [
    {
        "id": "IDEA-001", "date": "2026-06-01",
        "text": "Build a buyer-agent onboarding skill for DVN Coaching clients",
        "category": "Coaching", "priority": "High", "status": "New",
        "project": "call-coach-skill", "tags": ["coaching", "onboarding"], "source": "code",
    },
    {
        "id": "IDEA-002", "date": "2026-06-10",
        "text": "Add equity-alert trigger to database-coi: flag homeowners at 40%+ equity for outreach",
        "category": "VNRE", "priority": "Normal", "status": "In Progress",
        "project": "database-coi-skill", "tags": ["equity", "coi", "fub"], "source": "cowork",
    },
    {
        "id": "IDEA-003", "date": "2026-06-20",
        "text": "Weekly AI digest email to clients — market data + one insight — via content-engine",
        "category": "Marketing", "priority": "Low", "status": "Parked",
        "project": "", "tags": ["email", "content"], "source": "code",
    },
]


def selftest() -> None:
    print("Running self-test …")

    # next_id
    assert next_id([]) == "IDEA-001", "next_id empty failed"
    assert next_id(SELFTEST_IDEAS) == "IDEA-004", "next_id sequence failed"

    # make_idea
    idea = make_idea("Test idea", "VNRE", "Normal", "test-proj", ["a", "b"], "code", [])
    assert idea["id"] == "IDEA-001"
    assert idea["status"] == "New"
    assert idea["tags"] == ["a", "b"]

    # build_html
    html = build_html(SELFTEST_IDEAS, "2026-06-26")
    assert "DVN Ideas Vault" in html
    assert "IDEA-001" in html
    assert "IDEA-002" in html
    assert "equity-alert" in html
    assert "__IDEAS_JSON__" not in html  # placeholders replaced
    assert "__GENERATED__" not in html

    # round-trip via temp file
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as tf:
        json.dump(SELFTEST_IDEAS, tf)
        tmp_json = Path(tf.name)
    loaded = load(tmp_json)
    assert len(loaded) == 3
    tmp_json.unlink()

    print("PASS — all checks OK")

# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    p = argparse.ArgumentParser(description="Ideas Vault capture script")
    p.add_argument("--text",         help="Idea text (required for capture)")
    p.add_argument("--category",     choices=CATEGORIES, default="Other")
    p.add_argument("--priority",     choices=PRIORITIES, default="Normal")
    p.add_argument("--project",      default="",   help="Optional project name")
    p.add_argument("--tags",         default="",   help="Comma-separated tags")
    p.add_argument("--source",       choices=SOURCES, default="code")
    p.add_argument("--data",         type=Path, default=DEFAULT_DATA,
                   help="Path to ideas.json")
    p.add_argument("--html",         type=Path, default=DEFAULT_HTML,
                   help="Path to write ideas-master.html")
    p.add_argument("--update",       metavar="IDEA_ID",
                   help="Update an existing idea by ID")
    p.add_argument("--status",       choices=STATUSES,
                   help="New status for --update")
    p.add_argument("--rebuild-html", action="store_true",
                   help="Rebuild HTML from existing data, no new idea")
    p.add_argument("--selftest",     action="store_true")
    args = p.parse_args()

    if args.selftest:
        selftest()
        sys.exit(0)

    ideas = load(args.data)

    if args.update:
        # status update for an existing idea
        target = args.update.upper()
        match = [i for i in ideas if i["id"] == target]
        if not match:
            print(f"ERROR: {target} not found", file=sys.stderr)
            sys.exit(1)
        if not args.status:
            print("ERROR: --status required with --update", file=sys.stderr)
            sys.exit(1)
        for idea in ideas:
            if idea["id"] == target:
                idea["status"] = args.status
                print(f"{target} → {args.status}")
        save(ideas, args.data)
        write_html(ideas, args.html)
        print(f"HTML rebuilt → {args.html}")
        sys.exit(0)

    if args.rebuild_html:
        write_html(ideas, args.html)
        print(f"HTML rebuilt ({len(ideas)} ideas) → {args.html}")
        sys.exit(0)

    if not args.text:
        p.error("--text is required to capture a new idea")

    tags = [t for t in args.tags.split(",") if t.strip()]
    idea = make_idea(args.text, args.category, args.priority,
                     args.project, tags, args.source, ideas)
    ideas.append(idea)
    save(ideas, args.data)
    write_html(ideas, args.html)

    print(f"{idea['id']} captured ({idea['category']} · {idea['priority']}) → {args.html}")


if __name__ == "__main__":
    main()
