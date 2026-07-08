#!/usr/bin/env bash
#
# Local equivalent of .github/workflows/ci.yml (job: build).
# Run it directly, or let the pre-push hook run it (see .pre-commit-config.yaml).
#
# It uses `uv` to spin up an isolated Python 3.12 environment (CI pins 3.12),
# builds the distributions, validates them with twine, installs the wheel, and
# builds every example site — exactly what CI does. Build artifacts go to
# .cache/ (gitignored), so a staged release dist/ is never clobbered.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 99

if ! command -v uv >/dev/null 2>&1; then
  echo "error: 'uv' is required (https://docs.astral.sh/uv/). Install it and retry." >&2
  exit 2
fi

VENV=".cache/ci-venv"
DIST=".cache/ci-dist"
STATUS=0
step() { printf '\n########## %s ##########\n' "$1"; }
fail() { echo ">>> FAILED: $1 (exit $2)"; STATUS=1; }

step "env: python 3.12 (matches CI)"
uv venv --python 3.12 "$VENV" >/dev/null || { echo "venv create failed" >&2; exit 98; }
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python --version

step "install build + twine"
uv pip install --quiet build twine || fail "pip install build twine" $?

step "python -m build"
rm -rf "$DIST"
python -m build --outdir "$DIST" || fail "python -m build" $?

step "twine check"
twine check "$DIST"/* || fail "twine check" $?

step "install the wheel"
uv pip install --quiet "$DIST"/*.whl || fail "pip install wheel" $?

step "zensical build: examples/minimal"
zensical build -f examples/minimal/zensical.toml || fail "zensical build minimal" $?

step "zensical build: examples/basic"
zensical build -f examples/basic/zensical.toml || fail "zensical build basic" $?

# Don't leave generated example sites in the working tree.
rm -rf examples/*/site site

printf '\n'
if [ "$STATUS" -eq 0 ]; then
  echo "===== CI parity: ALL GREEN ====="
else
  echo "===== CI parity: FAILURES ABOVE — push blocked ====="
fi
exit "$STATUS"
