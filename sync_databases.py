"""
sync_databases.py
-----------------
Bidirectionally syncs the research database (CSV files) between:
  - Automating agent : .../automating agent/database/
  - Product scanner  : .../product scanner/database/

Rule: for each CSV, the newer file wins and overwrites the older one.
After syncing, commits and pushes both Git repos.

Usage:
    python sync_databases.py
    python sync_databases.py --dry-run   # preview only, no writes
    python sync_databases.py --no-git    # sync files only, skip git commit/push
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent          # DTI Automation/
AGENT_DB  = BASE / "automating agent" / "database"
SCANNER_DB = BASE / "product scanner" / "database"

AGENT_REPO   = BASE / "automating agent"
SCANNER_REPO = BASE / "product scanner"

# ── Helpers ────────────────────────────────────────────────────────────────────
def mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0

def fmt(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "—"

def run(cmd: list, cwd: Path):
    """Run a shell command and print output."""
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    return result.returncode

def git_push(repo: Path, label: str, dry: bool):
    """Stage all CSV changes, commit, and push."""
    print(f"\n{'[DRY RUN] ' if dry else ''}-- Git: {label} ({repo.name}) --")

    # Check for anything to commit
    status = subprocess.run(
        ["git", "status", "--porcelain", "database/"],
        cwd=str(repo), capture_output=True, text=True
    ).stdout.strip()

    if not status:
        print("  Nothing to commit — database already up-to-date.")
        return

    print(f"  Changed files:\n" + "\n".join(f"    {l}" for l in status.splitlines()))
    if dry:
        return

    run(["git", "add", "database/"], repo)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    run(["git", "commit", "-m", f"sync: update database CSVs ({ts})"], repo)
    rc = run(["git", "push"], repo)
    if rc != 0:
        print(f"  ⚠  Push failed for {label}. Check credentials / branch protection.")

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview only - no file writes or git operations")
    parser.add_argument("--no-git",  action="store_true", help="Sync files only, skip git commit/push")
    args = parser.parse_args()
    dry = args.dry_run

    if dry:
        print("=== DRY RUN - no files will be changed ===\n")

    # Collect all CSV filenames from both directories
    agent_files   = {f.name for f in AGENT_DB.glob("*.csv")}
    scanner_files = {f.name for f in SCANNER_DB.glob("*.csv")}
    all_files = agent_files | scanner_files

    copied = 0
    skipped = 0

    print(f"Syncing {len(all_files)} CSV files between:\n"
          f"  A: {AGENT_DB}\n"
          f"  B: {SCANNER_DB}\n")

    for name in sorted(all_files):
        a = AGENT_DB   / name
        b = SCANNER_DB / name

        mt_a = mtime(a)
        mt_b = mtime(b)

        if mt_a == 0:
            # Only in scanner → copy to agent
            action = f"B->A  {name}  (only in scanner, {fmt(mt_b)})"
            if not dry:
                shutil.copy2(str(b), str(a))
            copied += 1
        elif mt_b == 0:
            # Only in agent → copy to scanner
            action = f"A->B  {name}  (only in agent, {fmt(mt_a)})"
            if not dry:
                shutil.copy2(str(a), str(b))
            copied += 1
        elif mt_a > mt_b:
            action = f"A->B  {name}  (agent newer: {fmt(mt_a)} > {fmt(mt_b)})"
            if not dry:
                shutil.copy2(str(a), str(b))
            copied += 1
        elif mt_b > mt_a:
            action = f"B->A  {name}  (scanner newer: {fmt(mt_b)} > {fmt(mt_a)})"
            if not dry:
                shutil.copy2(str(b), str(a))
            copied += 1
        else:
            action = f"=    {name}  (identical timestamps - skipped)"
            skipped += 1

        print(f"  {action}")

    print(f"\nDone: {copied} file(s) synced, {skipped} already in sync.")

    # ── Git push both repos ────────────────────────────────────────────────────
    if not args.no_git:
        git_push(AGENT_REPO,   "CosmoTox (research)",    dry)
        git_push(SCANNER_REPO, "CosmoTox-App (scanner)", dry)
    else:
        print("\nSkipping git (--no-git flag set).")

    print("\nAll done.")

if __name__ == "__main__":
    main()
