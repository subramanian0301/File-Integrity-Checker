# File Integrity Checker

A beginner-friendly cybersecurity mini-project that detects unauthorized
or unexpected file changes inside a directory, using SHA-256 hashing.
This is the same core idea behind production tools like **Tripwire** and
**AIDE**: take a trusted "fingerprint" snapshot of a set of files, then
periodically compare it against the current state to catch tampering.

## How it works (architecture)

```
            ┌─────────────┐
            │   main.py   │   ← you run this; CLI menu
            └──────┬──────┘
                    │
        ┌───────────┼────────────┐
        ▼           ▼            ▼
┌──────────────┐ ┌──────────┐ ┌─────────────┐
│ scanner.py   │ │hasher.py │ │ verifier.py │
│ walks the    │ │computes  │ │ compares    │
│ folder tree  │ │SHA-256   │ │ snapshots + │
│              │ │per file  │ │ logs/alerts │
└──────────────┘ └──────────┘ └─────────────┘
```

- **hasher.py** — the smallest building block. Given one file path, it
  reads the file in small chunks and returns its SHA-256 hash. Reading
  in chunks (instead of all at once) means it won't run out of memory
  on huge files.
- **scanner.py** — walks an entire folder (including sub-folders) using
  `os.walk()`, calls `hasher.py` on every file it finds, and returns one
  dictionary: `{relative_file_path: hash}`.
- **verifier.py** — the decision-making layer. It can save a scan to
  `baseline.json`, load it back later, compare two scans to find
  modified/deleted/added files, and write timestamped results to
  `integrity_log.txt` while printing alerts to the terminal.
- **main.py** — the entry point. It just wires the three modules
  together behind a simple CLI/interactive menu: "baseline" or "check".

Keeping each concern in its own file means you can test, reuse, or swap
out any one piece (e.g. switch SHA-256 for SHA-3 in `hasher.py`)
without touching the others.

## Step-by-step setup

1. **Get the files.** Put `main.py`, `scanner.py`, `hasher.py`, and
   `verifier.py` in the same folder (this also applies to the optional
   `realtime_monitor.py`, `email_alert.py`, `gui.py` if you want them).
2. **Check your Python version** (3.7+ recommended):
   ```bash
   python3 --version
   ```
3. **(Optional)** Install the one extra dependency, only needed for
   real-time monitoring:
   ```bash
   pip install -r requirements.txt
   ```
4. **Create your first baseline** — this is your "known good" snapshot:
   ```bash
   python3 main.py baseline
   # then type the folder path you want to protect, e.g.: /home/user/important_docs
   ```
   This creates `baseline.json` in the same folder as the script.
5. **Check for changes** whenever you want (run this anytime — after a
   suspected incident, on a schedule via cron/Task Scheduler, etc.):
   ```bash
   python3 main.py check
   # type the same folder path again
   ```
   This prints alerts to the terminal and appends results to
   `integrity_log.txt`.
6. **(Optional) Real-time monitoring** — watch the folder live instead
   of running `check` manually:
   ```bash
   python3 realtime_monitor.py
   ```
7. **(Optional) GUI version** — a simple point-and-click interface:
   ```bash
   python3 gui.py
   ```
8. **(Optional) Email alerts** — open `email_alert.py`, fill in your
   sender/receiver email and an **app password** (never your real
   password), then call `send_alert_email(changes)` from `main.py`
   after `log_changes(changes)`.

## Sample output (verified by actually running the project)

**Step 1 — building the baseline** on a test folder containing
`file1.txt`, `config.cfg`, and `subfolder/nested.txt`:

```
=======================================================
        FILE INTEGRITY CHECKER
=======================================================
Enter the full path of the directory to scan: test_target
[*] Scanning 'test_target' to build a new baseline...
[OK] Baseline saved to 'baseline.json' (3 files recorded).
```

**Step 2 — after editing `file1.txt`, deleting `config.cfg`, and adding
a new file `new_suspicious_file.exe`**, running a check:

```
=======================================================
        FILE INTEGRITY CHECKER
=======================================================
Enter the full path of the directory to scan: test_target
[*] Re-scanning 'test_target' for changes...
[ALERT] [MODIFIED] file1.txt
[ALERT] [DELETED] config.cfg
[ALERT] [ADDED] new_suspicious_file.exe
```

**Resulting `integrity_log.txt` entry:**

```
--- Integrity Check: 2026-06-19 05:06:13 ---
[MODIFIED] file1.txt
[DELETED] config.cfg
[ADDED] new_suspicious_file.exe
```

**Step 3 — re-running with no changes** (after re-baselining) shows the
clean/safe state:

```
[*] Re-scanning 'test_target' for changes...
[2026-06-19 05:06:20] No changes detected. Everything looks safe.
```

## Notes & next steps

- `baseline.json` and `integrity_log.txt` are excluded from scans
  automatically so the tool never flags its own output files.
- For real protection, store `baseline.json` somewhere the attacker
  can't also modify (e.g. a read-only location, a separate machine, or
  print/commit a copy of its hash elsewhere) — otherwise an attacker
  who changes a file could also just update the baseline to match.
- Good next features to try adding yourself: scheduling automatic
  checks (cron / Task Scheduler), hashing file *metadata* (permissions,
  owner) in addition to content, or storing multiple historical
  baselines instead of overwriting the last one.
