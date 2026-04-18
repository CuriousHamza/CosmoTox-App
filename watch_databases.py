"""
watch_databases.py
------------------
File watcher that monitors both database folders for CSV changes.
When any CSV is modified or created in either folder, it waits 5 seconds
(to let batch writes settle) then runs sync_databases.py automatically.

Usage:
    python watch_databases.py          # runs until Ctrl+C
    python watch_databases.py --no-git # sync files only, skip git push
"""

import sys
import time
import argparse
import subprocess
import threading
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

BASE        = Path(__file__).resolve().parent.parent
AGENT_DB    = BASE / "automating agent" / "database"
SCANNER_DB  = BASE / "product scanner"  / "database"
SYNC_SCRIPT = BASE / "product scanner"  / "sync_databases.py"

DEBOUNCE_SECONDS = 5   # wait this long after last change before syncing


class DatabaseChangeHandler(FileSystemEventHandler):
    def __init__(self, label: str, no_git: bool):
        self.label  = label
        self.no_git = no_git
        self._timer: threading.Timer | None = None
        self._lock  = threading.Lock()

    def on_any_event(self, event):
        # Only care about CSV files (not directory events, not temp files)
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() != ".csv":
            return
        if path.name.startswith("~") or path.name.startswith("."):
            return

        print(f"[{self.label}] Change detected: {path.name} ({event.event_type})")
        self._schedule_sync()

    def _schedule_sync(self):
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(DEBOUNCE_SECONDS, self._run_sync)
            self._timer.start()
            print(f"  Sync scheduled in {DEBOUNCE_SECONDS}s (debounce reset)...")

    def _run_sync(self):
        print("\n[sync] Running sync_databases.py ...")
        cmd = [sys.executable, str(SYNC_SCRIPT)]
        if self.no_git:
            cmd.append("--no-git")
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode == 0:
            print("[sync] Done.\n")
        else:
            print(f"[sync] sync_databases.py exited with code {result.returncode}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-git", action="store_true",
                        help="Sync files only, skip git commit/push")
    args = parser.parse_args()

    for folder in (AGENT_DB, SCANNER_DB):
        if not folder.exists():
            print(f"ERROR: database folder not found: {folder}")
            sys.exit(1)

    handler_a = DatabaseChangeHandler("agent",   args.no_git)
    handler_b = DatabaseChangeHandler("scanner", args.no_git)

    observer = Observer()
    observer.schedule(handler_a, str(AGENT_DB),   recursive=False)
    observer.schedule(handler_b, str(SCANNER_DB), recursive=False)
    observer.start()

    print("Database watcher started.")
    print(f"  Watching: {AGENT_DB}")
    print(f"  Watching: {SCANNER_DB}")
    print(f"  Debounce: {DEBOUNCE_SECONDS}s")
    print("  Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        observer.stop()
    observer.join()
    print("Watcher stopped.")


if __name__ == "__main__":
    main()
