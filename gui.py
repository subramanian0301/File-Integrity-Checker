"""
gui.py   (OPTIONAL / ADVANCED FEATURE)
------------------------------------------
A simple graphical front-end for the File Integrity Checker, built with
Tkinter — Python's built-in GUI library (no extra install required,
unlike watchdog).

RUN:
    python gui.py
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from scanner import scan_directory
from verifier import save_baseline, load_baseline, compare_hashes, log_changes

# Keep track of which folder the user picked, shared across button callbacks
selected_directory = {"path": ""}


def choose_folder():
    """Open the OS's native folder picker dialog."""
    folder = filedialog.askdirectory()
    if folder:
        selected_directory["path"] = folder
        folder_label.config(text=f"Selected: {folder}")


def create_baseline_action():
    """Button callback: scan the chosen folder and save it as the baseline."""
    folder = selected_directory["path"]
    if not folder:
        messagebox.showwarning("No folder", "Please choose a folder first.")
        return

    hashes = scan_directory(folder)
    save_baseline(hashes)
    output_box.insert(tk.END, f"Baseline created for {len(hashes)} files.\n")
    output_box.see(tk.END)  # auto-scroll to the latest line


def check_changes_action():
    """Button callback: re-scan the folder and compare against the baseline."""
    folder = selected_directory["path"]
    if not folder:
        messagebox.showwarning("No folder", "Please choose a folder first.")
        return

    old_hashes = load_baseline()
    if old_hashes is None:
        messagebox.showerror("No baseline", "Create a baseline first.")
        return

    new_hashes = scan_directory(folder)
    changes = compare_hashes(old_hashes, new_hashes)
    log_changes(changes)

    output_box.insert(tk.END, "\n--- Check Result ---\n")
    if not any(changes.values()):
        output_box.insert(tk.END, "No changes detected. Everything looks safe.\n")
    else:
        for kind in ("modified", "deleted", "added"):
            for path in changes[kind]:
                output_box.insert(tk.END, f"[{kind.upper()}] {path}\n")

    output_box.see(tk.END)


# --- Build the window ---
root = tk.Tk()
root.title("File Integrity Checker")
root.geometry("540x440")

tk.Button(root, text="1. Choose Folder", command=choose_folder, width=25).pack(pady=6)
folder_label = tk.Label(root, text="No folder selected", fg="gray")
folder_label.pack()

tk.Button(root, text="2. Create Baseline", command=create_baseline_action, width=25).pack(pady=6)
tk.Button(root, text="3. Check for Changes", command=check_changes_action, width=25).pack(pady=6)

output_box = scrolledtext.ScrolledText(root, width=64, height=15)
output_box.pack(pady=10, padx=10)

if __name__ == "__main__":
    root.mainloop()
