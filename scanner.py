"""
scanner.py
----------
This module walks through a target directory (including every
sub-folder inside it) and builds a dictionary that maps each file's
path to its SHA-256 hash.

This dictionary is the core data structure of the whole project:
- The FIRST time you scan, this dictionary becomes the "baseline"
  (the trusted, known-good snapshot of the folder).
- EVERY TIME AFTER, this same function is used to take a fresh
  snapshot, which gets compared against the baseline to spot changes.
"""

import os
from hasher import calculate_file_hash

# Files belonging to the checker itself — we never want to hash our own
# baseline or log file, otherwise the tool would flag itself as "changed"
# every time it runs.
IGNORED_FILES = {"baseline.json", "integrity_log.txt"}


def scan_directory(directory_path):
    """
    Recursively scan every file inside `directory_path` and calculate
    a SHA-256 hash for each one.

    Parameters:
        directory_path (str): The root folder to scan.

    Returns:
        dict: { "relative/path/to/file.txt": "hash_value", ... }

        NOTE: Paths are stored RELATIVE to `directory_path` (using
        forward slashes) rather than as full absolute paths. This way,
        the baseline still works correctly even if you rename the
        parent folder or move it somewhere else on disk.
    """
    file_hashes = {}

    if not os.path.isdir(directory_path):
        print(f"[ERROR] '{directory_path}' is not a valid directory.")
        return file_hashes

    # os.walk() recursively visits the root folder and every sub-folder.
    # For each one it gives us: (current_folder, list_of_subfolders, list_of_files)
    for current_folder, _sub_folders, file_names in os.walk(directory_path):

        for file_name in file_names:
            if file_name in IGNORED_FILES:
                continue  # skip the checker's own output files

            full_path = os.path.join(current_folder, file_name)

            # Convert to a path relative to the scanned folder, and
            # normalize slashes so the baseline is portable across
            # Windows ("\\") and Mac/Linux ("/").
            relative_path = os.path.relpath(full_path, directory_path).replace("\\", "/")

            file_hash = calculate_file_hash(full_path)

            # Only record files we successfully managed to hash.
            if file_hash is not None:
                file_hashes[relative_path] = file_hash

    return file_hashes
