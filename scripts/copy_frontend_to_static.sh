#!/usr/bin/env bash
# Build frontend and copy frontend/dist into STATIC_ROOT defined in Django settings.
# Usage: run from repo root or just execute this script. Ensure your venv is activated
# if you need a specific Python interpreter.
#
# This script:
#  - builds the frontend using bun/npm/pnpm (in that order)
#  - copies all files from frontend/dist into Django's STATIC_ROOT (reads from settings)
#  - preserves relative layout and file metadata where possible
#  - prints a summary and exits non-zero on failure

set -euo pipefail

# Resolve repo root (script located at inventory/scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "Working directory: $REPO_ROOT"

# 1) Build frontend
if [ -d "frontend" ]; then
  echo "Building frontend..."
  pushd frontend >/dev/null
  if command -v bun >/dev/null 2>&1; then
    echo "Using bun to build"
    bun run build
  elif command -v pnpm >/dev/null 2>&1; then
    echo "Using pnpm to build"
    pnpm run build
  elif command -v npm >/dev/null 2>&1; then
    echo "Using npm to build"
    npm run build
  else
    echo "No bun/pnpm/npm found in PATH. Install one or run the frontend build manually." >&2
    popd >/dev/null || true
    exit 1
  fi
  popd >/dev/null
else
  echo "frontend directory not found, skipping build step."
fi

# 2) Copy frontend/dist -> STATIC_ROOT using Django settings
echo "Copying frontend/dist to Django STATIC_ROOT..."

python - <<'PY'
from pathlib import Path
import shutil, os, sys

# Ensure Python can import the Django project. Try several candidate locations for the project package
repo_root = Path.cwd()
candidates = [
    repo_root,
    repo_root / 'backend',
    repo_root / 'inventory' / 'backend',
    repo_root / 'src' / 'backend',
]
inserted = False
for candidate in candidates:
    # look for the inner package dir (contains __init__.py) or a settings.py directly
    if (candidate / 'backend' / '__init__.py').exists() or (candidate / '__init__.py').exists() or (candidate / 'settings.py').exists():
        sys.path.insert(0, str(candidate.resolve()))
        inserted = True
        break
if not inserted:
    # fallback: add repo root so at least relative imports from repo root might work
    sys.path.insert(0, str(repo_root))

# Ensure Django settings are available
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    import django
    django.setup()
except Exception as e:
    print("Failed to setup Django. Make sure your venv is activated and dependencies are installed.", file=sys.stderr)
    print("Error:", e, file=sys.stderr)
    sys.exit(2)

from django.conf import settings

src = Path('frontend/dist')
dst = Path(settings.STATIC_ROOT)

if not src.exists() or not src.is_dir():
    print(f"Source frontend build not found at: {src}", file=sys.stderr)
    sys.exit(3)

dst.mkdir(parents=True, exist_ok=True)

total = 0
skipped = 0

for p in sorted(src.rglob('*')):
    rel = p.relative_to(src)
    target = dst / rel
    try:
        if p.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        total += 1
    except Exception as e:
        print(f"SKIP {rel} -> {e}", file=sys.stderr)
        skipped += 1

print(f"Copied {total} files from {src} to {dst}")
if skipped:
    print(f"Skipped {skipped} files (see errors above)", file=sys.stderr)

PY

echo "Done."
