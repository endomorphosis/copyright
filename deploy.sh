#!/usr/bin/env bash
set -euo pipefail

# Deploy script: rebuild everything and push to both repos
#
# Steps:
#   1. Run tests to ensure data integrity
#   2. Prepare act-snapshot data from version histories
#   3. Build the copyright-history git repo (one commit per act)
#   4. Build the static website into docs/
#   5. Push copyright-history repo to GitHub
#   6. Commit and push this repo (with updated docs/) to GitHub

cd "$(dirname "$0")"

echo "=== Step 1: Running tests ==="
python3 -m pytest tests/test_todo_tasks.py tests/test_substantive.py tests/test_data_integrity.py tests/test_version_chains.py tests/test_audit.py --tb=short -q
echo

echo "=== Step 2: Preparing build data ==="
python3 prepare_build_data.py
echo

echo "=== Step 3: Building copyright-history repo ==="
python3 build.py
echo

echo "=== Step 4: Building website ==="
python3 build_site.py
echo

echo "=== Step 5: Pushing copyright-history repo ==="
cd ~/code/copyright-history
git push -f origin main
cd - >/dev/null
echo

echo "=== Step 6: Committing and pushing this repo ==="
git add docs/
if git diff --cached --quiet; then
    echo "No website changes to commit."
else
    git commit -m "Rebuild website from latest data

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
fi
git push origin main
echo

echo "=== Deploy complete ==="
echo "  copyright-history: https://github.com/katelynsills/copyright-history"
echo "  website:           https://katelynsills.com/copyright/"
