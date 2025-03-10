import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
import threading
import json

def show_help():
    """Opens a Toplevel window with short documentation about the app."""
    help_win = tk.Toplevel()
    help_win.title("Help / Documentation")
    help_win.iconphoto(False, tk.PhotoImage(file="hvx.png"))
    help_win.geometry("450x550")
    help_text = (
        "File Organizer Help\n"
        "--------------------\n"
        "This application sorts your clips based on a naming convention:\n\n"
        "  DATE_CATEGORY_SPOT_PERSON_ORGNAME\n\n"
        "Parts:\n"
        "  • DATE (export date): e.g. 20230115\n"
        "  • CATEGORY: L, F, B, or A (if merging L/F). L = Landed, F = Failed,\n"
        "    B = B-roll (no person), A = A-roll (consolidated from L/F).\n"
        "  • SPOT (skate spot name).\n"
        "  • PERSON (skater's name or identifier).\n"
        "  • ORGNAME (original filename or whatever else follows).\n\n"
        "RULES:\n"
        "  • A-roll (L or F) includes a person. B-roll doesn't have a person.\n"
        "  • If 'Merge L/F -> A' is checked, L and F become 'A' during sorting.\n"
        "  • B-roll (B) is distinct and lacks a 'person'.\n\n"
        "APP USAGE:\n"
        "1) 'Input Dir': folder containing your clips.\n"
        "2) 'Output Dir': where sorted clips go, unless 'Modify in place' is checked.\n"
        "3) 'Sort Order': choose how to build subfolders (e.g. date, spot, category,\n"
        "   person, etc.). If blank, everything goes to the root directory.\n"
        "4) 'Merge L/F -> A': merges landed/failed categories into 'A' for A-roll.\n"
        "5) 'Modify in place': moves files within the Input Dir.\n"
        "6) 'Start' button: processes files. Errors show at the bottom if any.\n\n"
        "TIPS:\n"
        "  - If a file doesn't meet the naming convention or category is invalid,\n"
        "    it goes to the errors list.\n"
        "  - B-roll won't have a person in the name. L/F/A do have 'person'.\n"
    )

    lbl = tk.Label(help_win, text=help_text, justify="left")
    lbl.pack(padx=10, pady=10, fill="both", expand=True)


def load_sort_values_json():
    with open("sort_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

def get_category(cat, merge_l_f):
    if merge_l_f and cat in ("L", "F"):
        return "A"
    if cat in ("L", "F", "B"):
        return cat
    return None

def get_all_files(directory):
    files = []
    for root, _, filenames in os.walk(directory):
        for f in filenames:
            files.append(os.path.join(root, f))
    return files

def remove_empty_dirs(path, skip_root):
    for entry in os.scandir(path):
        if entry.is_dir():
            remove_empty_dirs(entry.path, skip_root=False)
    if not skip_root and not any(os.scandir(path)):
        os.rmdir(path)

def process_files(in_dir, out_dir, sorting_criteria, merge_l_f, modify_in_place,
                  progress_bar, status_label, error_lbl, error_text, root):

    # Hide + clear old errors
    error_lbl.grid_remove()
    error_text.grid_remove()
    error_text.config(state="normal")
    error_text.delete("1.0", tk.END)
    error_text.config(state="disabled")

    if not modify_in_place:
        Path(out_dir).mkdir(parents=True, exist_ok=True)

    all_files = get_all_files(in_dir)
    total = len(all_files)
    error_log = []

    no_subfolders = (len(sorting_criteria) == 1 and not sorting_criteria[0].strip())

    for idx, file_path in enumerate(all_files):
        filename_only = os.path.basename(file_path)
        parts = filename_only.split("_")

        try:
            if len(parts) < 3:
                error_log.append((filename_only, "Not enough underscore parts"))
                continue

            date_val = parts[0]
            cat = parts[1]
            rest = parts[2:]

            category = get_category(cat, merge_l_f)
            if not category:
                error_log.append((filename_only, f"Invalid category '{cat}'"))
                continue

            if category == "B":
                if len(rest) < 2:
                    error_log.append((filename_only, "Insufficient parts for B"))
                    continue
                data_map = {"date": date_val, "spot": rest[0], "category": "B"}
            else:
                if len(rest) < 3:
                    error_log.append((filename_only, "Insufficient parts for A/L/F"))
                    continue
                data_map = {
                    "date": date_val,
                    "spot": rest[0],
                    "category": category,
                    "person": rest[1]
                }

            base_dir = in_dir if modify_in_place else out_dir
            if no_subfolders:
                target_folder = base_dir
            else:
                subdirs = []
                for c in sorting_criteria:
                    key = c.strip()
                    if key in data_map:
                        subdirs.append(data_map[key])
                target_folder = os.path.join(base_dir, *subdirs)

            Path(target_folder).mkdir(parents=True, exist_ok=True)
            destination = os.path.join(target_folder, filename_only)

            if modify_in_place:
                shutil.move(file_path, destination)
            else:
                shutil.copy2(file_path, destination)

        except Exception as e:
            error_log.append((filename_only, str(e)))

        progress_bar["value"] = ((idx + 1) / total) * 100
        status_label.config(text=f"Processing: {idx + 1}/{total}")

    messagebox.showinfo("Done", f"Processing complete. {len(error_log)} errors.")
    status_label.config(text="Ready")

    # If there are errors, show + populate the error box
    if error_log:
        error_text.config(state="normal")
        for fname, reason in error_log:
            error_text.insert(tk.END, f"- {fname}: {reason}\n")
        error_text.config(state="disabled")

        # Show the error widgets
        error_lbl.grid()
        error_text.grid()

        root.update_idletasks()
        root.geometry("")

    if modify_in_place:
        remove_empty_dirs(in_dir, skip_root=True)

def select_input_dir():
    input_var.set(filedialog.askdirectory())

def select_output_dir():
    output_var.set(filedialog.askdirectory())

def toggle_out_dir_state():
    if in_place_var.get():
        out_entry.config(state="disabled")
        out_btn.config(state="disabled")
    else:
        out_entry.config(state="normal")
        out_btn.config(state="normal")

def run_processing():
    if not input_var.get() or (not output_var.get() and not in_place_var.get()):
        messagebox.showerror("Error", "Select input + output directories (unless modifying in place).")
        return

    order = [x.strip() for x in sort_var.get().split(",")]
    progress_bar["value"] = 0
    status_label.config(text="Processing...")

    threading.Thread(
        target=process_files,
        args=(
            input_var.get(),
            output_var.get(),
            order,
            merge_var.get(),
            in_place_var.get(),
            progress_bar,
            status_label,
            error_lbl,
            error_text,
            root
        ),
        daemon=True
    ).start()

# ---------------- GUI ----------------

root = tk.Tk()
root.title("File Organizer")
root.geometry("540x280")
root.iconphoto(False, tk.PhotoImage(file="hvx.png"))

main_frm = tk.Frame(root)
main_frm.pack(expand=True, fill="both")

box_frm = tk.Frame(main_frm)
box_frm.pack(anchor="center", pady=5)

input_var = tk.StringVar()
output_var = tk.StringVar()
sort_var = tk.StringVar(value="spot, category")
merge_var = tk.BooleanVar(value=True)
in_place_var = tk.BooleanVar(value=False)

# ----- Row 0: Input Directory -----
tk.Label(box_frm, text="Input Dir:", anchor="e").grid(row=0, column=0, sticky="e", padx=5, pady=3)
in_entry = tk.Entry(box_frm, textvariable=input_var, width=35)
in_entry.grid(row=0, column=1, sticky="w", padx=5, pady=3)
in_btn = tk.Button(box_frm, text="Browse", command=select_input_dir)
in_btn.grid(row=0, column=2, padx=5, pady=3)

# ----- Row 1: Output Directory -----
tk.Label(box_frm, text="Output Dir:", anchor="e").grid(row=1, column=0, sticky="e", padx=5, pady=3)
out_entry = tk.Entry(box_frm, textvariable=output_var, width=35)
out_entry.grid(row=1, column=1, sticky="w", padx=5, pady=3)
out_btn = tk.Button(box_frm, text="Browse", command=select_output_dir)
out_btn.grid(row=1, column=2, padx=5, pady=3)

# ----- Row 2: Sort Order -----
tk.Label(box_frm, text="Sort Order:", anchor="e").grid(row=2, column=0, sticky="e", padx=5, pady=3)
sort_cb = ttk.Combobox(
    box_frm, textvariable=sort_var, state="readonly", width=33,
    values=load_sort_values_json()
)
sort_cb.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=3)

# ----- Row 3: Merge Check -----
tk.Label(box_frm, text="Merge L/F -> A:", anchor="e").grid(row=3, column=0, sticky="e", padx=5, pady=3)
merge_chk = tk.Checkbutton(box_frm, variable=merge_var)
merge_chk.grid(row=3, column=1, sticky="w", padx=5, pady=3)

# ----- Row 4: Modify In Place -----
tk.Label(box_frm, text="Modify in place:", anchor="e").grid(row=4, column=0, sticky="e", padx=5, pady=3)
in_place_chk = tk.Checkbutton(box_frm, variable=in_place_var, command=toggle_out_dir_state)
in_place_chk.grid(row=4, column=1, sticky="w", padx=5, pady=3)

# ----- Row 5: Start & Help Buttons -----
start_btn = tk.Button(box_frm, text="Start", width=10, command=run_processing)
start_btn.grid(row=5, column=0, sticky="e", padx=5, pady=5)

help_btn = tk.Button(box_frm, text="Help", width=10, command=show_help)
help_btn.grid(row=5, column=1, sticky="w", padx=5, pady=5)

# ----- Row 6: Progress Bar -----
progress_bar = ttk.Progressbar(box_frm, orient="horizontal", mode="determinate")
progress_bar.grid(row=6, column=0, columnspan=3, sticky="ew", padx=5, pady=3)

# ----- Row 7: Status Label -----
status_label = tk.Label(box_frm, text="Ready", anchor="center")
status_label.grid(row=7, column=0, columnspan=3, padx=5, pady=(0, 5))

# ----- Rows 8+9: Error Widgets (Hidden initially) -----
error_lbl = tk.Label(box_frm, text="Errors:", anchor="w")
error_lbl.grid(row=8, column=0, columnspan=3, sticky="w", padx=5, pady=(0, 2))
error_lbl.grid_remove()   # hide initially

error_text = ScrolledText(box_frm, height=6, width=58, wrap="word", state="disabled")
error_text.grid(row=9, column=0, columnspan=3, sticky="ew", padx=5, pady=(0, 10))
error_text.grid_remove()  # hide initially

box_frm.grid_columnconfigure(1, weight=1)

root.mainloop()
