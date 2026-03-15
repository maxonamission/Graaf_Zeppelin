#!/usr/bin/env bash
# Security checks for Graaf Zeppelin (S11-05)
# Run: bash scripts/security_check.sh

set -euo pipefail

REPORT_DIR="reports"
mkdir -p "$REPORT_DIR"

echo "=== Graaf Zeppelin Security Checks ==="
echo ""

# 1. Bandit — Python SAST
echo "[1/3] Running bandit (Python security linter)..."
if command -v bandit &>/dev/null; then
    bandit -r app/ -f json -o "$REPORT_DIR/bandit.json" --severity-level medium 2>/dev/null || true
    bandit -r app/ -f txt --severity-level medium 2>/dev/null || true
    echo "  -> Report saved to $REPORT_DIR/bandit.json"
else
    echo "  -> SKIPPED: bandit not installed (pip install bandit)"
fi
echo ""

# 2. pip-audit — Dependency CVE check
echo "[2/3] Running pip-audit (dependency vulnerabilities)..."
if command -v pip-audit &>/dev/null; then
    pip-audit --format json --output "$REPORT_DIR/pip-audit.json" 2>/dev/null || true
    pip-audit 2>/dev/null || true
    echo "  -> Report saved to $REPORT_DIR/pip-audit.json"
else
    echo "  -> SKIPPED: pip-audit not installed (pip install pip-audit)"
fi
echo ""

# 3. Check for common secrets in codebase
echo "[3/3] Checking for potential secrets in code..."
SECRETS_FOUND=0
for pattern in "password\s*=" "secret.*=.*['\"]" "api_key\s*=\s*['\"]sk-" "BEGIN.*PRIVATE KEY"; do
    if grep -rn --include="*.py" "$pattern" app/ 2>/dev/null | grep -v "test_" | grep -v "__pycache__" | grep -v ".pyc"; then
        SECRETS_FOUND=1
    fi
done
if [ "$SECRETS_FOUND" -eq 0 ]; then
    echo "  -> No hardcoded secrets detected"
fi
echo ""

echo "=== Security checks complete ==="
echo "Reports saved to $REPORT_DIR/"
