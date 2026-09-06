
# apps/core/utils/generate_folder_structure.py

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


DEFAULT_NAME_EXCLUSIONS = [".idea", ".venv", ".git", "__pycache__", "migrations", "media"]
DEFAULT_EXT_EXCLUSIONS = [".mp3", ".torrent", ".jpg", ".jpeg", ".png", ".gif", ".webp"]


def normalize_path(path):
    return os.path.abspath(os.path.expanduser(str(path)))


def _normalize_ext(ext: str) -> str:
    ext = ext.strip().lower()
    if not ext:
        return ext
    return ext if ext.startswith(".") else f".{ext}"


def _parse_list(value: str) -> list[str]:
    parts = []
    for item in value.split(";"):
        item = item.strip()
        if item:
            parts.append(item)
    return parts


def _should_skip_file_by_ext(path: str, ext_exclusions: set[str]) -> bool:
    suffix = Path(path).suffix.lower()
    return suffix in ext_exclusions


def _sort_entries(entries: list[str], directory_path: str, sort_mode: str) -> list[str]:
    if sort_mode == "name":
        return sorted(entries, key=lambda x: x.lower())

    if sort_mode in {"created", "modified"}:
        reverse = False
        key_func = None

        if sort_mode == "created":
            key_func = lambda x: os.path.getctime(os.path.join(directory_path, x))
        elif sort_mode == "modified":
            key_func = lambda x: os.path.getmtime(os.path.join(directory_path, x))

        return sorted(entries, key=lambda x: (key_func(x), x.lower()), reverse=reverse)

    return sorted(entries, key=lambda x: x.lower())


def print_tree(
    path,
    abs_exclusions,
    name_exclusions,
    ext_exclusions=None,
    prefix="",
    is_last=True,
    output_lines=None,
    sort_mode="name",
    level=0,
    sort_second_level_only=False,
):
    if output_lines is None:
        output_lines = []

    if ext_exclusions is None:
        ext_exclusions = set()

    abs_path = os.path.abspath(path)
    name = os.path.basename(path)

    if abs_path in abs_exclusions:
        return output_lines

    show_only_folder = name in name_exclusions and os.path.isdir(path)
    connector = "└── " if is_last else "├── "

    if name == "":
        output_lines.append(abs_path.upper())
    else:
        output_lines.append(
            f"{prefix}{connector}{name}{' [содержимое скрыто]' if show_only_folder else ''}"
        )

    if show_only_folder:
        return output_lines

    new_prefix = prefix + ("    " if is_last else "│   ")

    try:
        entries = os.listdir(path)
    except PermissionError:
        output_lines.append(f"{new_prefix}<Недостаточно прав для {name}>")
        return output_lines

    filtered_entries = []
    for entry in entries:
        entry_path = os.path.abspath(os.path.join(path, entry))
        if entry_path in abs_exclusions:
            continue
        if os.path.isfile(entry_path) and _should_skip_file_by_ext(entry_path, ext_exclusions):
            continue
        filtered_entries.append(entry)

    dirs = [e for e in filtered_entries if os.path.isdir(os.path.join(path, e))]
    files = [e for e in filtered_entries if os.path.isfile(os.path.join(path, e))]

    if sort_second_level_only and level >= 1:
        dirs = _sort_entries(dirs, path, sort_mode)
    else:
        dirs = sorted(dirs, key=lambda x: x.lower())

    files = sorted(files, key=lambda x: x.lower())

    for i, file in enumerate(files):
        is_last_file = (i == len(files) - 1) and (len(dirs) == 0)
        file_connector = "└── " if is_last_file else "├── "
        output_lines.append(f"{new_prefix}{file_connector}{file}")

    for i, directory in enumerate(dirs):
        is_last_dir = (i == len(dirs) - 1)
        print_tree(
            os.path.join(path, directory),
            abs_exclusions,
            name_exclusions,
            ext_exclusions=ext_exclusions,
            prefix=new_prefix,
            is_last=is_last_dir,
            output_lines=output_lines,
            sort_mode=sort_mode,
            level=level + 1,
            sort_second_level_only=sort_second_level_only,
        )

    return output_lines


def generate_tree_report(
    base_path,
    abs_exclusions,
    name_exclusions,
    output_file,
    ext_exclusions=None,
    sort_mode="name",
    sort_second_level_only=False,
):
    base_path = normalize_path(base_path)
    output_file = normalize_path(output_file)

    if ext_exclusions is None:
        ext_exclusions = []

    ext_exclusions = {_normalize_ext(ext) for ext in ext_exclusions if ext.strip()}

    lines = print_tree(
        base_path,
        abs_exclusions,
        name_exclusions,
        ext_exclusions=ext_exclusions,
        sort_mode=sort_mode,
        sort_second_level_only=sort_second_level_only,
    )

    with open(output_file, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    return lines


def launch_gui():
    root = tk.Tk()
    root.title("Folder Structure Generator")
    root.geometry("980x820")

    base_path_var = tk.StringVar()
    output_path_var = tk.StringVar()
    abs_exclusions_var = tk.StringVar()
    name_exclusions_var = tk.StringVar(value="; ".join(DEFAULT_NAME_EXCLUSIONS))
    ext_exclusions_var = tk.StringVar(value="; ".join(DEFAULT_EXT_EXCLUSIONS))
    sort_mode_var = tk.StringVar(value="name")
    second_level_sort_var = tk.BooleanVar(value=False)

    def choose_base():
        p = filedialog.askdirectory(title="Выберите базовую папку")
        if p:
            base_path_var.set(p)

    def choose_output():
        p = filedialog.asksaveasfilename(
            title="Сохранить отчет",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="folder_structure.txt",
        )
        if p:
            output_path_var.set(p)

    def run_generate():
        base_path = base_path_var.get().strip()
        output_path = output_path_var.get().strip()

        if not base_path:
            messagebox.showwarning("Ошибка", "Выберите базовую папку.")
            return

        if not output_path:
            messagebox.showwarning("Ошибка", "Выберите файл для сохранения отчёта.")
            return

        abs_exclusions = [x.strip() for x in abs_exclusions_var.get().split(";") if x.strip()]
        name_exclusions = [x.strip() for x in name_exclusions_var.get().split(";") if x.strip()]
        ext_exclusions = [x.strip() for x in ext_exclusions_var.get().split(";") if x.strip()]

        try:
            lines = generate_tree_report(
                base_path=base_path,
                abs_exclusions=abs_exclusions,
                name_exclusions=name_exclusions,
                output_file=output_path,
                ext_exclusions=ext_exclusions,
                sort_mode=sort_mode_var.get(),
                sort_second_level_only=second_level_sort_var.get(),
            )
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return

        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "\n".join(lines))
        messagebox.showinfo("Готово", f"Отчёт создан:\n{output_path}")

    form = tk.Frame(root)
    form.pack(fill="x", padx=10, pady=10)

    tk.Label(form, text="Базовая папка:").grid(row=0, column=0, sticky="w")
    tk.Entry(form, textvariable=base_path_var, width=90).grid(row=1, column=0, sticky="we", pady=2)
    tk.Button(form, text="Выбрать", command=choose_base).grid(row=1, column=1, padx=5)

    tk.Label(form, text="Файл отчёта:").grid(row=2, column=0, sticky="w", pady=(10, 0))
    tk.Entry(form, textvariable=output_path_var, width=90).grid(row=3, column=0, sticky="we", pady=2)
    tk.Button(form, text="Сохранить как", command=choose_output).grid(row=3, column=1, padx=5)

    tk.Label(form, text="Абсолютные исключения (через ';'):").grid(row=4, column=0, sticky="w", pady=(10, 0))
    tk.Entry(form, textvariable=abs_exclusions_var, width=90).grid(row=5, column=0, sticky="we", pady=2)

    tk.Label(form, text="Исключения по именам папок (через ';'):").grid(row=6, column=0, sticky="w", pady=(10, 0))
    tk.Entry(form, textvariable=name_exclusions_var, width=90).grid(row=7, column=0, sticky="we", pady=2)

    tk.Label(form, text="Исключения по расширениям файлов (через ';', например .mp3; .jpg):").grid(row=8, column=0, sticky="w", pady=(10, 0))
    tk.Entry(form, textvariable=ext_exclusions_var, width=90).grid(row=9, column=0, sticky="we", pady=2)

    sort_frame = tk.Frame(form)
    sort_frame.grid(row=10, column=0, sticky="w", pady=(10, 0))

    tk.Label(sort_frame, text="Сортировка директорий:").pack(side="left")
    tk.Radiobutton(sort_frame, text="по имени", variable=sort_mode_var, value="name").pack(side="left", padx=5)
    tk.Radiobutton(sort_frame, text="по дате создания", variable=sort_mode_var, value="created").pack(side="left", padx=5)
    tk.Radiobutton(sort_frame, text="по дате обновления", variable=sort_mode_var, value="modified").pack(side="left", padx=5)
    tk.Checkbutton(sort_frame, text="только второй уровень", variable=second_level_sort_var).pack(side="left", padx=15)

    tk.Button(root, text="Сгенерировать", command=run_generate, bg="#4CAF50", fg="white").pack(pady=10)

    result_text = ScrolledText(root, height=30)
    result_text.pack(fill="both", expand=True, padx=10, pady=10)

    root.mainloop()


def main():
    launch_gui()


if __name__ == "__main__":
    main()
