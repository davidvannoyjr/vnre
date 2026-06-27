# vnre-fob-mpc-top-leases — FOB MPC Check

On-demand market pulse: top 3 lease listings in FUB this week, ranked by list price.

## Files
```
fob-mpc-top-leases-skill/
├── SKILL.md                        # skill definition + in-session steps
├── README.md                       # this file
├── config.example.json             # copy → config.json, fill in FUB details
├── scripts/build_top_leases.py     # standalone FUB pull + filter + rank + render
└── sample/sample_deals.json        # representative deals for testing
```

## Try it (no network)
```bash
python3 scripts/build_top_leases.py --selftest
```

## Run it (networked Mac)
```bash
cp config.example.json config.json   # fill in apiKeyFile
FUB_API_KEY=xxx python3 scripts/build_top_leases.py \
  --config config.json \
  --out "$(date +%F) MPC Top Leases.md"
cat "$(date +%F) MPC Top Leases.md"
```

## Ranking
`price desc → created desc`. Lease match: deal `type` or `tags` in `leaseTypes`.
Week window: Monday 00:00 → Sunday 23:59 of the current week.
Tune `leaseTypes`, `activeStages`, and `topN` in `config.json`.

## In-session (Cowork / no outbound network)
Use `fub_*` MCP tools (load via ToolSearch). Pull deals, filter to lease type + this week,
rank, present inline. See `SKILL.md §Steps` for the full flow.
