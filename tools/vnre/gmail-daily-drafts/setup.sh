#!/usr/bin/env bash
# Gmail Daily Draft Prep — Mac installer
# Run once: bash setup.sh
# Safe to re-run; existing config/.env/auth are never overwritten.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$HOME/automations/gmail-daily-drafts"
PLIST_NAME="com.dvn.gmail-daily-drafts"
PLIST_TEMPLATE="$SCRIPT_DIR/${PLIST_NAME}.plist.template"
PLIST_DEST="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

echo ""
echo "=== Gmail Daily Draft Prep — Setup ==="
echo "Deploy dir: $DEPLOY_DIR"
echo ""

# ------------------------------------------------------------------
# 1. Verify the deploy path is NOT inside Google Drive
# ------------------------------------------------------------------
ABS_DEPLOY="$(python3 -c "import os; print(os.path.realpath('$DEPLOY_DIR'))" 2>/dev/null || echo "$DEPLOY_DIR")"
if echo "$ABS_DEPLOY" | grep -qiE "google.?drive|googledrive|com~apple~clouddocs|icloud|dropbox|onedrive"; then
    echo "ERROR: Deploy path appears inside a cloud-sync folder: $ABS_DEPLOY"
    echo "       Move DEPLOY_DIR to a non-synced location (e.g. ~/automations/)."
    exit 1
fi
echo "✓ $DEPLOY_DIR is outside cloud sync."

# ------------------------------------------------------------------
# 2. Create directory structure
# ------------------------------------------------------------------
mkdir -p "$DEPLOY_DIR/auth" "$DEPLOY_DIR/logs"
echo "✓ Directories created."

# ------------------------------------------------------------------
# 3. Copy/update source files (never overwrite config or auth)
# ------------------------------------------------------------------
cp "$SCRIPT_DIR/daily_draft_prep.py" "$DEPLOY_DIR/daily_draft_prep.py"
cp "$SCRIPT_DIR/requirements.txt"    "$DEPLOY_DIR/requirements.txt"

if [ ! -f "$DEPLOY_DIR/config.json" ]; then
    cp "$SCRIPT_DIR/config.example.json" "$DEPLOY_DIR/config.json"
    echo "✓ config.json installed from example."
else
    echo "✓ config.json already exists (not overwritten)."
fi
echo "✓ Script files copied."

# ------------------------------------------------------------------
# 4. Python virtual environment + dependencies
# ------------------------------------------------------------------
if [ ! -d "$DEPLOY_DIR/venv" ]; then
    python3 -m venv "$DEPLOY_DIR/venv"
    echo "✓ Python venv created."
fi
"$DEPLOY_DIR/venv/bin/pip" install -q --upgrade pip
"$DEPLOY_DIR/venv/bin/pip" install -q -r "$DEPLOY_DIR/requirements.txt"
echo "✓ Python dependencies installed."

# ------------------------------------------------------------------
# 5. Create .env if it doesn't exist
# ------------------------------------------------------------------
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    cat > "$DEPLOY_DIR/.env" << 'EOF'
# Anthropic API key — get from https://console.anthropic.com
ANTHROPIC_API_KEY=PASTE_YOUR_KEY_HERE
EOF
    echo "✓ .env created — edit $DEPLOY_DIR/.env and add your ANTHROPIC_API_KEY before first run."
else
    echo "✓ .env already exists (not overwritten)."
fi

# ------------------------------------------------------------------
# 6. Install launchd plist
# ------------------------------------------------------------------
sed \
    -e "s|__HOME__|${HOME}|g" \
    -e "s|__DEPLOY_DIR__|${DEPLOY_DIR}|g" \
    "$PLIST_TEMPLATE" \
    > "$PLIST_DEST"

# Unload stale version if present, then load fresh
launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load -w "$PLIST_DEST"
echo "✓ launchd job installed and loaded."

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
echo ""
echo "=== Setup complete ==="
echo ""
echo "NEXT STEPS (required before the job fires):"
echo ""
echo "  1. Add your Anthropic API key:"
echo "       open $DEPLOY_DIR/.env"
echo "     Replace PASTE_YOUR_KEY_HERE with your key from https://console.anthropic.com"
echo ""
echo "  2. Add Gmail OAuth credentials:"
echo "       a. Go to https://console.cloud.google.com"
echo "       b. APIs & Services → Credentials → Create → OAuth 2.0 Client ID"
echo "       c. Application type: Desktop app"
echo "       d. Download JSON → save to $DEPLOY_DIR/auth/credentials.json"
echo ""
echo "  3. Authorize Gmail (opens browser once, then auto-refreshes forever):"
echo "       cd $DEPLOY_DIR && venv/bin/python3 daily_draft_prep.py"
echo ""
echo "  4. Edit config to add your active clients and leads:"
echo "       open $DEPLOY_DIR/config.json"
echo ""
echo "  Job fires daily at 6:30 AM."
echo "  Logs: $DEPLOY_DIR/logs/"
echo ""
echo "  To run manually any time:"
echo "       cd $DEPLOY_DIR && venv/bin/python3 daily_draft_prep.py"
echo ""
echo "  To unload: launchctl unload $PLIST_DEST"
echo "  To reload: launchctl load -w $PLIST_DEST"
echo ""
