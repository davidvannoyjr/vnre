# Gmail Daily Draft Prep

Runs every morning at 6:30 AM on the Mac Studio via launchd. Reads the Gmail inbox for
the last 24 hours, generates reply drafts in DVN's voice via Claude API, and saves them
as native Gmail drafts. Does not send anything.

---

## What it does

1. **Fetches** all inbox messages from the last 24 hours that are not from you.
2. **Filters out** newsletters, receipts, no-reply senders, calendar invites, automated
   notifications, and threads where you already sent the last message.
3. **Prioritizes** by category: active clients/transactions → leads → coaching clients →
   vendors/partners → everything else. Caps at 15 drafts (configurable).
4. **Generates** a reply draft in DVN's voice for each one using `claude-opus-4-8`.
5. **Saves** each draft to the correct Gmail thread (Drafts folder). Nothing is sent.
6. **Logs** a plain-text summary: sender, subject, one-line gist, and priority category.

---

## Where everything lives

```
~/automations/gmail-daily-drafts/       ← deploy root (NOT in Google Drive)
  daily_draft_prep.py                   ← main script
  config.json                           ← classification config (edit freely)
  requirements.txt                      ← Python dependencies
  .env                                  ← ANTHROPIC_API_KEY (never commit this)
  auth/
    credentials.json                    ← Google OAuth client secrets (never commit)
    token.json                          ← OAuth token (auto-created + auto-refreshed)
  logs/
    YYYY-MM-DD-draft-prep.log           ← full run log
    YYYY-MM-DD-summary.txt              ← daily summary (sender, subject, gist)
    launchd-out.log                     ← launchd stdout capture
    launchd-err.log                     ← launchd stderr capture
  venv/                                 ← Python virtual environment

~/Library/LaunchAgents/
  com.dvn.gmail-daily-drafts.plist      ← launchd schedule (installed by setup.sh)
```

Source code lives in the `vnre` GitHub repo at `tools/vnre/gmail-daily-drafts/`.
Deploy to the Mac by running `setup.sh` from the cloned repo.

---

## One-time setup

### 1. Get an Anthropic API key

Go to [https://console.anthropic.com](https://console.anthropic.com), create a key, and
add it to `~/.automations/gmail-daily-drafts/.env`:

```
ANTHROPIC_API_KEY=sk-ant-XXXX
```

### 2. Set up Gmail OAuth credentials

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com).
2. Create a project (or select an existing one).
3. Enable the **Gmail API**: APIs & Services → Library → Gmail API → Enable.
4. Create credentials: APIs & Services → Credentials → **+ Create Credentials** →
   OAuth 2.0 Client ID → Application type: **Desktop app**.
5. Download the JSON file. Save it to:
   ```
   ~/automations/gmail-daily-drafts/auth/credentials.json
   ```

### 3. Run setup.sh

From the cloned repo:

```bash
bash tools/vnre/gmail-daily-drafts/setup.sh
```

This copies the script, creates the Python venv, installs deps, and loads the launchd job.

### 4. Authorize Gmail (one-time browser flow)

```bash
cd ~/automations/gmail-daily-drafts
venv/bin/python3 daily_draft_prep.py
```

A browser window opens. Sign in as `david@vannoyre.com` and grant access.
The token is saved to `auth/token.json` and auto-refreshed from then on.

---

## Edit the config

`~/automations/gmail-daily-drafts/config.json` controls all classification logic (copied
from `config.example.json` during setup). Reload is automatic — changes take effect on
the next run with no restart.

```jsonc
{
  "lookback_hours": 24,        // how far back to look (hours)
  "draft_cap": 15,             // max drafts per run

  "no_reply_patterns": [...],  // regex patterns — matching senders are skipped
  "subject_block_keywords": [...],  // substring keywords — matching subjects skipped
  "sender_blocklist": [...],   // exact email addresses to always skip

  "active_clients": [          // email fragments — matched against sender address
    "client@example.com"
  ],
  "leads": [
    "lead@example.com"
  ],
  "coaching_clients": [
    "coachingclient@example.com"
  ],
  "vendors_partners": [
    "title", "mortgage"        // substring matches — e.g. "title" matches any @titleco.com
  ]
}
```

Priority order: active_clients > leads > coaching_clients > vendors_partners > other.

---

## Run manually at any time

```bash
cd ~/automations/gmail-daily-drafts
venv/bin/python3 daily_draft_prep.py
```

### Dry run (no drafts saved to Gmail)

```bash
venv/bin/python3 daily_draft_prep.py --dry-run
```

---

## Re-authorize Gmail

If the token expires and can't auto-refresh (e.g. credentials revoked):

```bash
cd ~/automations/gmail-daily-drafts
venv/bin/python3 daily_draft_prep.py --reauth
```

The browser opens. Sign in again. New token is saved automatically.

The log will show this error clearly if it ever happens:
```
GMAIL AUTH EXPIRED — could not auto-refresh
Fix: run  python3 daily_draft_prep.py --reauth
```

---

## Check the schedule

```bash
# See if the job is loaded
launchctl list | grep gmail-daily-drafts

# View next fire time
launchctl print gui/$(id -u)/com.dvn.gmail-daily-drafts
```

---

## Disable / uninstall

```bash
# Stop and disable the schedule (job won't fire until re-loaded)
launchctl unload ~/Library/LaunchAgents/com.dvn.gmail-daily-drafts.plist

# Full uninstall
launchctl unload ~/Library/LaunchAgents/com.dvn.gmail-daily-drafts.plist
rm ~/Library/LaunchAgents/com.dvn.gmail-daily-drafts.plist
# Keep ~/automations/gmail-daily-drafts/ for logs; delete it if you want a clean slate.
```

---

## Update the script

Pull the latest from the repo and re-run setup:

```bash
cd ~/vnre   # or wherever you cloned the repo
git pull
bash tools/vnre/gmail-daily-drafts/setup.sh
```

The setup script never overwrites `config.json`, `.env`, or `auth/`.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| "GMAIL AUTH EXPIRED" in log | `python3 daily_draft_prep.py --reauth` |
| "ANTHROPIC_API_KEY not set" | Edit `~/.automations/gmail-daily-drafts/.env` |
| Job not running at 6:30 AM | `launchctl list \| grep gmail` — if missing, re-run `setup.sh` |
| Drafts not appearing | Check `logs/YYYY-MM-DD-draft-prep.log` for errors |
| Too many / too few drafts | Edit `draft_cap`, blocklists, and patterns in `config.json` |
| Mac was off at 6:30 AM | launchd will NOT catch up if the Mac was powered off (only catches up from sleep) |
