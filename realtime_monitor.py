"""
realtime_monitor.py   (OPTIONAL / ADVANCED FEATURE)
-----------------------------------------------------
The core project (main.py) checks for changes only when YOU run it.
This module instead watches a folder LIVE and reacts the instant a
file is created, modified, or deleted — no need to manually re-run
anything.

This relies on the third-party 'watchdog' library, which uses your
operating system's native file-event notifications (instead of
constantly re-scanning the folder, which would be slow and wasteful).

INSTALL FIRST:
    pip install watchdog

RUN:
    python realtime_monitor.py
"""

import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG_FILE = "integrity_log.txt"


class IntegrityEventHandler(FileSystemEventHandler):
    """
    Watchdog calls the matching method below automatically whenever a
    file event happens. We override the ones we care about.
    """

    def _record(self, action, path):
        """Shared helper: print an alert and append it to the log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [REALTIME-{action}] {path}"
        print(f"[ALERT] {line}")
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")

    def on_created(self, event):
        if not event.is_directory:
            self._record("ADDED", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._record("DELETED", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._record("MODIFIED", event.src_path)


def start_monitoring(directory):
    """
    Begin watching `directory` (and its sub-folders) continuously.
    Keeps running until the user presses Ctrl+C.
    """
    event_handler = IntegrityEventHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()

    print(f"[*] Real-time monitoring started on '{directory}'.")
    print("[*] Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)  # keep the main thread alive; watchdog runs in the background
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] Monitoring stopped by user.")

    observer.join()


if __name__ == "__main__":
    folder = input("Enter the folder to monitor in real time: ").strip()
    start_monitoring(folder)
