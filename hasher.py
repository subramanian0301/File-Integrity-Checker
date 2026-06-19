"""
hasher.py
---------
This module has exactly ONE job: calculate the SHA-256 hash of a file's
content.

WHAT IS A HASH?
A hash is like a digital fingerprint of a file. Feed a file's bytes into
a hash function and you get back a fixed-length string (64 hex characters
for SHA-256). If even a single byte inside the file changes, the
resulting hash changes completely and unpredictably. This makes hashing
the perfect tool for detecting tampering: instead of comparing entire
files byte-by-byte, we just compare their short hash fingerprints.

WHY SHA-256 SPECIFICALLY?
- It is cryptographically strong (practically impossible to find two
  different files that produce the same hash, a.k.a. a "collision").
- It is fast enough to run on thousands of files without noticeable lag.
- It's the de-facto standard used in real security tools (Tripwire,
  AIDE, git, package managers, etc.).
"""

import hashlib


def calculate_file_hash(file_path, chunk_size=4096):
    """
    Calculate the SHA-256 hash of a single file.

    We read the file in small chunks (4 KB at a time by default) instead
    of loading the entire file into memory in one go. This means the
    function works fine even on huge files (videos, ISOs, databases)
    without consuming gigabytes of RAM.

    Parameters:
        file_path (str): Full path to the file we want to hash.
        chunk_size (int): How many bytes to read per chunk. Default 4096.

    Returns:
        str: The SHA-256 hash as a 64-character hexadecimal string.
        None: If the file could not be read (permission error, the file
              was deleted mid-scan, it's a broken symlink, etc.) — we
              don't want one bad file to crash the whole scan.
    """
    sha256_hash = hashlib.sha256()  # start a new, empty SHA-256 "calculator"

    try:
        # "rb" = read in binary mode. Hashing works on raw bytes, not text,
        # so this is required for it to work correctly on ANY file type
        # (images, PDFs, executables, zip files, plain text, etc.).
        with open(file_path, "rb") as f:
            # Keep reading chunks until we hit an empty chunk (b""),
            # which signals end-of-file.
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(chunk)  # feed this chunk into the hash

        return sha256_hash.hexdigest()  # final fingerprint, as readable hex

    except (IOError, OSError, PermissionError) as error:
        print(f"[ERROR] Could not read file '{file_path}': {error}")
        return None
