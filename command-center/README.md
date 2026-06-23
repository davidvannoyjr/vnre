# command-center — the niched daily screen

The 5 AM go/no-go. One screen, one question: *what do I do today to hit the plan.*
Read-only — it displays what the skills already compute; it scores nothing.

```
command-center/
├── index.html        # the single-pane shell (four panels)
├── data.example.json # live-data shape
└── README.md         # this file
```

## Run it
- Open `index.html` — it renders with embedded sample data.
- Live: `index.html?data=path/to/today.json` (built to `data.example.json` shape).

## The four panels (hard cap — see the brief)
1. **Today's Hunt** ← `vnre-active-hunter`
2. **Needs Attention** ← `daily-lead-attention`
3. **Pace vs Plan** ← the numbers math (50 contacts → 1 appt → ~70% → listing; 75/yr)
4. **Pipeline — LA: Appointments** ← `vnre-book-appointment`

A fifth panel = a new niche. Don't add — fork a second center.

## Brand
Red `#C8102E` accent only; charcoal/gray base; Roboto Condensed headers. Matches
the offer-summary / `vnre-html-branding` palette (master manual §7).

## Wiring (to go live)
Point each morning task's JSON output into one merged `today.json` (or four files
and a tiny loader). The center fetches and renders — no build step, no server
required. Brief: [`../claude/01-projects/niched-command-center/CLAUDE.md`](../claude/01-projects/niched-command-center/CLAUDE.md).
