"""Lexicon: local-first vocabulary with SM-2-inspired reviews. Python 3.10+."""
import json
import math
import os
import time
import uuid
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path

MODES = ("direct", "aligned", "expression")
def now():
    return int(time.time() * 1000)

def validate(data):
    if data.get("version") != 1 or not isinstance(data.get("name"), str) or not isinstance(data.get("items"), list):
        raise ValueError("Not a Lexicon version 1 dictionary.")
    for x in data["items"]:
        for k in ("id", "source", "target"):
            if not isinstance(x.get(k), str):
                raise ValueError("Invalid entry text.")
        if x.get("mode") not in MODES:
            raise ValueError("Invalid translation mode.")
        if not isinstance(x.get("alignment"), list) or not isinstance(x.get("history"), list):
            raise ValueError("Invalid alignment or history.")
        for k in ("created", "due", "interval", "ease", "repetitions"):
            v = x.get(k)
            if not isinstance(v, (int, float)) or not math.isfinite(v):
                raise ValueError("Invalid schedule.")
        if x["interval"] < 0 or x["ease"] < 1.3:
            raise ValueError("Invalid interval or ease.")
        targets = x["target"].split()
        for j in x["alignment"]:
            if not isinstance(j, int) or j < -1 or j >= len(targets):
                raise ValueError("Invalid word position.")
    return data

def schedule(item, quality):
    item["ease"] = max(1.3, item["ease"] + .1 - (5-quality)*(.08+(5-quality)*.02))
    if quality < 3:
        item["repetitions"] = 0
        item["interval"] = 0
        item["due"] = now() + 600000
    else:
        r = item["repetitions"]
        item["interval"] = 1 if r == 0 else 6 if r == 1 else max(1, int(item["interval"] * item["ease"] + .5))
        item["repetitions"] += 1
        item["due"] = now() + item["interval"] * 86400000
    item["history"].append({"at": now(), "quality": quality, "interval": item["interval"]})

class Lexicon:
    def __init__(self, root):
        self.root = root
        root.title("Lexicon • Your personal dictionary")
        root.geometry("980x650")
        root.minsize(700, 460)
        root.configure(bg="#f6f5ef")
        self.path = None
        self.data = {"version": 1, "name": "My dictionary", "items": []}
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f6f5ef")
        style.configure("TLabel", background="#f6f5ef", foreground="#25352e")
        style.configure("TButton", padding=9)
        style.configure("Treeview", rowheight=34)
        wrap = ttk.Frame(root, padding=24)
        wrap.pack(fill="both", expand=True)
        ttk.Label(wrap, text="Words worth remembering.", font=("Helvetica", 25, "bold")).pack(anchor="w")
        self.status = ttk.Label(wrap, text="Create or open a dictionary to get started.")
        self.status.pack(anchor="w", pady=(8, 18))
        bar = ttk.Frame(wrap)
        bar.pack(fill="x")
        for text, command in (("New dictionary", self.new), ("Open", self.open), ("Add word", self.add), ("Review due", self.review), ("Delete selected", self.delete)):
            ttk.Button(bar, text=text, command=command).pack(side="left", padx=(0, 8))
        self.search = tk.StringVar()
        search = ttk.Entry(wrap, textvariable=self.search)
        search.pack(fill="x", pady=15)
        self.search.trace_add("write", lambda *_: self.refresh())
        table = ttk.Frame(wrap)
        table.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(table, columns=("source", "target", "mode", "due"), show="headings")
        for key, title in (("source", "Word / expression"), ("target", "Translation"), ("mode", "Connection"), ("due", "Next review")):
            self.tree.heading(key, text=title)
            self.tree.column(key, width=200 if key in ("source", "target") else 130)
        scroll = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        root.after(200, self.setup)
        root.after(60000, self.tick)

    def setup(self):
        choice = messagebox.askyesnocancel("Your dictionary", "Create your own blank dictionary file?\n\nYes: create a file\nNo: open an existing file\nCancel: choose later")
        if choice is True:
            self.new()
        elif choice is False:
            self.open()

    def write(self):
        if not self.path:
            return False
        temp = self.path.with_name(self.path.name + ".tmp")
        try:
            temp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(temp, self.path)
            return True
        except OSError as exc:
            messagebox.showerror("Could not save", str(exc) + "\nYour changes remain in memory. Check file permissions and disk space.")
            return False

    def new(self):
        if self.path and not messagebox.askyesno("New dictionary", "Switch to a new blank dictionary? Your current file will not be changed."):
            return
        p = filedialog.asksaveasfilename(title="Create your blank dictionary", defaultextension=".json", filetypes=[("Lexicon dictionary", "*.json")])
        if not p:
            return
        old_path, old_data = self.path, self.data
        self.path = Path(p)
        self.data = {"version": 1, "name": self.path.stem, "items": []}
        if not self.write():
            self.path, self.data = old_path, old_data
        self.refresh()

    def open(self):
        p = filedialog.askopenfilename(filetypes=[("Lexicon dictionary", "*.json")])
        if not p:
            return
        try:
            data = validate(json.loads(Path(p).read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError, KeyError) as exc:
            messagebox.showerror("Could not open dictionary", str(exc))
            return
        self.path, self.data = Path(p), data
        self.refresh()

    def tick(self):
        self.refresh()
        self.root.after(60000, self.tick)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        query = self.search.get().casefold()
        for x in reversed(self.data["items"]):
            if query not in (x["source"] + " " + x["target"]).casefold():
                continue
            due = "Ready now" if x["due"] <= now() else datetime.fromtimestamp(x["due"]/1000).strftime("%b %d, %Y")
            self.tree.insert("", "end", iid=x["id"], values=(x["source"], x["target"], x["mode"], due))
        n = sum(x["due"] <= now() for x in self.data["items"])
        self.status.config(text=f'{self.data["name"]} • {len(self.data["items"])} words • {n} due for review' if self.path else "Create or open a dictionary to get started.")

    def add(self):
        if not self.path:
            messagebox.showinfo("Setup first", "Create or open a dictionary file first.")
            return
        win = tk.Toplevel(self.root)
        win.title("Add a discovery")
        win.transient(self.root)
        win.grab_set()
        form = ttk.Frame(win, padding=24)
        form.pack(fill="both", expand=True)
        source, target, mode = tk.StringVar(), tk.StringVar(), tk.StringVar(value="direct")
        for label, variable in (("Word or expression", source), ("Translation", target)):
            ttk.Label(form, text=label).pack(anchor="w", pady=(12, 5))
            ttk.Entry(form, textvariable=variable, width=55).pack(fill="x")
        ttk.Label(form, text="Translation connection").pack(anchor="w", pady=(12, 5))
        pick = ttk.Combobox(form, textvariable=mode, values=MODES, state="readonly")
        pick.pack(fill="x")
        align = ttk.Frame(form)
        align.pack(fill="x", pady=12)
        mappings = []
        def positions(*_):
            for child in align.winfo_children():
                child.destroy()
            mappings.clear()
            if mode.get() != "aligned":
                return
            targets = target.get().split()
            options = ["No direct match"] + [f"{j+1}: {w}" for j, w in enumerate(targets)]
            for i, word in enumerate(source.get().split()):
                row = ttk.Frame(align)
                row.pack(fill="x", pady=2)
                ttk.Label(row, text=word + " → ", width=20).pack(side="left")
                combo = ttk.Combobox(row, values=options, state="readonly")
                combo.current(i+1 if i < len(targets) else 0)
                combo.pack(side="left")
                mappings.append(combo)
        for variable in (source, target, mode):
            variable.trace_add("write", positions)
        ttk.Label(form, text="Direct = meaning · Aligned = word positions · Expression = whole idiom", wraplength=430).pack(anchor="w")
        def save():
            s, t = source.get().strip(), target.get().strip()
            if not s or not t:
                messagebox.showwarning("Missing text", "Enter both the word and its translation.", parent=win)
                return
            timestamp = now()
            item = {"id": str(uuid.uuid4()), "source": s, "target": t, "mode": mode.get(),
                    "alignment": [c.current()-1 for c in mappings], "created": timestamp,
                    "due": timestamp, "interval": 0, "ease": 2.5, "repetitions": 0, "history": []}
            self.data["items"].append(item)
            if self.write():
                win.destroy()
            else:
                self.data["items"].remove(item)
            self.refresh()
        ttk.Button(form, text="Save to dictionary", command=save).pack(anchor="e", pady=15)

    def delete(self):
        selected = set(self.tree.selection())
        if not selected or not messagebox.askyesno("Delete words", "Permanently delete selected entries?"):
            return
        old = self.data["items"]
        self.data["items"] = [x for x in old if x["id"] not in selected]
        if not self.write():
            self.data["items"] = old
        self.refresh()

    def review(self):
        due = sorted((x for x in self.data["items"] if x["due"] <= now()), key=lambda x: x["due"])
        if not due:
            messagebox.showinfo("All caught up", "No words are due right now.")
            return
        win = tk.Toplevel(self.root)
        win.title("Retrieval practice")
        win.geometry("620x380")
        win.transient(self.root)
        win.grab_set()
        frame = ttk.Frame(win, padding=30)
        frame.pack(fill="both", expand=True)
        def next_item():
            for child in frame.winfo_children():
                child.destroy()
            if not due:
                ttk.Label(frame, text="Session complete. Well done!").pack(pady=40)
                ttk.Button(frame, text="Close", command=win.destroy).pack()
                return
            x = due[0]
            ttk.Label(frame, text=f"{len(due)} remaining · Recall the translation").pack()
            ttk.Label(frame, text=x["source"], font=("Helvetica", 22, "bold"), wraplength=540).pack(pady=25)
            def reveal():
                reveal_button.destroy()
                ttk.Label(frame, text=x["target"], font=("Helvetica", 17), wraplength=540).pack(pady=12)
                if x["mode"] == "aligned":
                    s, t = x["source"].split(), x["target"].split()
                    text = " · ".join(f'{s[i]} → {t[j] if j >= 0 else "—"}' for i, j in enumerate(x["alignment"]) if i < len(s))
                    ttk.Label(frame, text=text, wraplength=540).pack()
                row = ttk.Frame(frame)
                row.pack(pady=15)
                def rate(q):
                    old = json.loads(json.dumps(x))
                    schedule(x, q)
                    if self.write():
                        due.pop(0)
                        self.refresh()
                        next_item()
                    else:
                        x.clear()
                        x.update(old)
                for label, q in (("Again", 1), ("Hard", 3), ("Good", 4), ("Easy", 5)):
                    ttk.Button(row, text=label, command=lambda q=q: rate(q)).pack(side="left", padx=5)
            reveal_button = ttk.Button(frame, text="Reveal meaning", command=reveal)
            reveal_button.pack()
        next_item()

if __name__ == "__main__":
    root = tk.Tk()
    Lexicon(root)
    root.mainloop()
