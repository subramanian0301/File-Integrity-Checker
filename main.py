"""
main.py
-------
This is the entry point of the File Integrity Checker. It ties together
hasher.py (hashing), scanner.py (walking the folder), and verifier.py
(comparing + logging) into one simple command-line tool.

USAGE:
    python main.py baseline      Scan a folder and save it as the baseline
    python main.py check         Re-scan a folder and compare it to the baseline

    python main.py               (no arguments) launches an interactive
                                  menu — easiest option for beginners.
"""

import sys
from scanner import scan_directory
from verifier import save_baseline, load_baseline, compare_hashes, log_changes


def create_baseline(directory):
    """Scan the directory fresh and save the result as the new baseline."""
    print(f"[*] Scanning '{directory}' to build a new baseline...")
    file_hashes = scan_directory(directory)

    if not file_hashes:
        print("[WARNING] No files were found/hashed. Baseline will be empty.")

    save_baseline(file_hashes)


def run_check(directory):
    """Re-scan the directory and compare the result against the saved baseline."""
    old_hashes = load_baseline()

    if old_hashes is None:
        print("[ERROR] No baseline found. Run option 1 / 'baseline' first.")
        return

    print(f"[*] Re-scanning '{directory}' for changes...")
    new_hashes = scan_directory(directory)

    changes = compare_hashes(old_hashes, new_hashes)
    log_changes(changes)


def main():
    print("=" * 55)
    print("        FILE INTEGRITY CHECKER")
    print("=" * 55)

    # Support BOTH styles of use:
    #   1) Command-line:  python main.py baseline
    #   2) Interactive menu (friendlier for beginners)
    if len(sys.argv) >= 2:
        command = sys.argv[1].strip().lower()
    else:
        print("1. Create baseline (first-time setup)")
        print("2. Check for changes (compare against baseline)")
        choice = input("Choose an option (1/2): ").strip()
        command = "baseline" if choice == "1" else "check"

    directory = input("Enter the full path of the directory to scan: ").strip()

    if command == "baseline":
        create_baseline(directory)
    elif command == "check":
        run_check(directory)
    else:
        print(f"[ERROR] Unknown command '{command}'. Use 'baseline' or 'check'.")


if __name__ == "__main__":
    main()
