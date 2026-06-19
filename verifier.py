"""
verifier.py
-----------
This module is the "brain" of the File Integrity Checker. It:

  1. Saves/loads the baseline.json file (our trusted snapshot).
  2. Compares an old snapshot against a new one to detect:
       - MODIFIED files (same path, different hash)
       - DELETED files  (in old snapshot, missing from new one)
       - ADDED files    (in new snapshot, wasn't in the old one)
  3. Writes a timestamped record of every change to integrity_log.txt
  4. Prints clear, readable alerts to the terminal.
"""

import json
import os
from datetime import datetime

BASELINE_FILE = "baseline.json"
LOG_FILE = "integrity_log.txt"


def save_baseline(file_hashes, baseline_path=BASELINE_FILE):
    """
    Save a dictionary of {file_path: hash} to a JSON file on disk so it
    can be reloaded later and used as the "known good" reference point.
    """
    with open(baseline_path, "w") as f:
        json.dump(file_hashes, f, indent=4, sort_keys=True)

    print(f"[OK] Baseline saved to '{baseline_path}' ({len(file_hashes)} files recorded).")


def load_baseline(baseline_path=BASELINE_FILE):
    """
    Load a previously saved baseline JSON file back into a dictionary.

    Returns:
        dict: The saved {file_path: hash} mapping.
        None: If no baseline file exists yet (caller should tell the
              user to create one first).
    """
    if not os.path.exists(baseline_path):
        return None

    with open(baseline_path, "r") as f:
        return json.load(f)


def compare_hashes(old_hashes, new_hashes):
    """
    Compare a baseline snapshot against a fresh snapshot.

    Parameters:
        old_hashes (dict): The trusted baseline {path: hash}.
        new_hashes (dict): The just-collected current scan {path: hash}.

    Returns:
        dict: {
            "modified": [list of file paths whose hash changed],
            "deleted":  [list of file paths missing from the new scan],
            "added":    [list of file paths that are brand new],
        }
    """
    modified = []
    deleted = []
    added = []

    # Walk through everything that WAS in the baseline...
    for path, old_hash in old_hashes.items():
        if path not in new_hashes:
            deleted.append(path)            # it's gone now
        elif new_hashes[path] != old_hash:
            modified.append(path)           # same name, different content

    # Anything in the new scan that the baseline never saw is brand new.
    for path in new_hashes:
        if path not in old_hashes:
            added.append(path)

    return {"modified": sorted(modified), "deleted": sorted(deleted), "added": sorted(added)}


def log_changes(changes, log_path=LOG_FILE):
    """
    Append a timestamped block describing detected changes to the log
    file, and print matching alerts to the terminal so the user notices
    immediately rather than only when they open the log later.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    has_changes = any(changes[key] for key in changes)

    with open(log_path, "a") as log:
        log.write(f"\n--- Integrity Check: {timestamp} ---\n")

        if not has_changes:
            log.write("No changes detected. All files match the baseline.\n")
            print(f"[{timestamp}] No changes detected. Everything looks safe.")
            return

        for path in changes["modified"]:
            line = f"[MODIFIED] {path}"
            log.write(line + "\n")
            print(f"[ALERT] {line}")

        for path in changes["deleted"]:
            line = f"[DELETED] {path}"
            log.write(line + "\n")
            print(f"[ALERT] {line}")

        for path in changes["added"]:
            line = f"[ADDED] {path}"
            log.write(line + "\n")
            print(f"[ALERT] {line}")
