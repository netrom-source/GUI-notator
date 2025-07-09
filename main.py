import os
import json
import random
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, simpledialog
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Tkinter is required to run this application. "
        "Install it with 'sudo apt-get install python3-tk' on Debian/Ubuntu."
    ) from exc


DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, "tabs_state.json")
QUOTES_FILE = os.path.join(DATA_DIR, "quotes.txt")


class NoteText(tk.Text):
    """Text widget with optional Hemingway mode."""

    def __init__(self, master, **kwargs):
        super().__init__(master, wrap=tk.WORD, undo=True, **kwargs)
        self.filename: str | None = None
        self.hemingway = False

    def enable_hemingway(self, enable: bool) -> None:
        self.hemingway = enable

    def _block_keys(self, event: tk.Event) -> str:
        if self.hemingway and event.keysym in {"BackSpace", "Delete", "Left"}:
            return "break"
        return ""


class GUINotator(tk.Tk):
    """Main application."""

    def __init__(self) -> None:
        super().__init__()
        self.title("GUI Notator")
        self.geometry("800x600")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.timer_label = tk.Label(self, text="", fg="green")
        self.timer_label.pack(side=tk.TOP, fill=tk.X)

        self.status = tk.Label(self, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.timer_id: str | None = None
        self.remaining = 0
        self.hemingway = False
        self.quotes = self._load_quotes()

        self._bind_shortcuts()
        self._load_tabs()

    # ---------- Utility methods ----------
    def _bind_shortcuts(self) -> None:
        self.bind("<Control-n>", lambda e: self.new_tab())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save())
        self.bind("<Control-S>", lambda e: self.save_as())
        self.bind("<Control-w>", lambda e: self.close_tab())
        self.bind("<Control-l>", lambda e: self.show_quote())
        self.bind("<Control-t>", lambda e: self.set_timer())
        self.bind("<Control-r>", lambda e: self.reset_timer())
        self.bind("<Control-g>", lambda e: self.toggle_hemingway())
        self.bind("<Control-Delete>", lambda e: self.delete_file())

    def _load_quotes(self) -> list[str]:
        if os.path.exists(QUOTES_FILE):
            with open(QUOTES_FILE, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        return []

    def _current_text(self) -> NoteText:
        frame = self.nametowidget(self.notebook.select())
        return frame.winfo_children()[0]

    # ---------- Tab management ----------
    def new_tab(self, filename: str | None = None, content: str | None = None) -> None:
        frame = tk.Frame(self.notebook)
        text = NoteText(frame)
        text.pack(fill=tk.BOTH, expand=True)
        text.bind("<Key>", text._block_keys, add=True)
        text.bind("<<Modified>>", lambda e, t=text: self._on_modified(t))
        if filename:
            text.filename = filename
        if content:
            text.insert("1.0", content)
        title = filename or "Untitled"
        self.notebook.add(frame, text=title)
        self.notebook.select(frame)

    def close_tab(self) -> None:
        current = self.notebook.select()
        if current:
            self.notebook.forget(current)

    def _on_modified(self, text: NoteText) -> None:
        idx = self.notebook.index(self.notebook.select())
        label = self.notebook.tab(idx, "text")
        if text.edit_modified():
            if not label.endswith("*"):
                self.notebook.tab(idx, text=label + "*")
        else:
            self.notebook.tab(idx, text=label.rstrip("*"))
        text.edit_modified(False)

    # ---------- File operations ----------
    def save(self) -> None:
        text = self._current_text()
        if not text.filename:
            self.save_as()
            return
        path = os.path.join(DATA_DIR, text.filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.get("1.0", tk.END))
        self.status.config(text=f"Saved {text.filename}")
        self._update_tab_title(text)
        text.edit_modified(False)

    def save_as(self) -> None:
        text = self._current_text()
        path = filedialog.asksaveasfilename(initialdir=DATA_DIR, defaultextension=".txt")
        if not path:
            return
        text.filename = os.path.basename(path)
        self.save()

    def open_file(self) -> None:
        path = filedialog.askopenfilename(initialdir=DATA_DIR, filetypes=[("Text", "*.txt")])
        if not path:
            return
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.new_tab(filename, content)

    def delete_file(self) -> None:
        text = self._current_text()
        if not text.filename:
            return
        if not messagebox.askyesno("Delete", f"Delete {text.filename}?"):
            return
        haiku = [simpledialog.askstring("Haiku", f"Line {i+1}") for i in range(3)]
        if not all(haiku):
            return
        counts = [len(line.split()) for line in haiku]
        if counts != [5, 7, 5]:
            messagebox.showerror("Haiku", "Haiku must be 5,7,5 words")
            return
        os.remove(os.path.join(DATA_DIR, text.filename))
        self.close_tab()
        self.status.config(text="File deleted")

    def _update_tab_title(self, text: NoteText) -> None:
        idx = self.notebook.index(self.notebook.select())
        title = text.filename or "Untitled"
        self.notebook.tab(idx, text=title)

    # ---------- Timer ----------
    def set_timer(self) -> None:
        minutes = simpledialog.askinteger("Timer", "Minutes:", minvalue=1, maxvalue=120)
        if not minutes:
            return
        self.remaining = minutes * 60
        self._tick_timer()

    def _tick_timer(self) -> None:
        mins, sec = divmod(self.remaining, 60)
        self.timer_label.config(text=f"{mins:02d}:{sec:02d}")
        if self.remaining <= 0:
            self.status.config(text="Timer finished")
            return
        self.remaining -= 1
        self.timer_id = self.after(1000, self._tick_timer)

    def reset_timer(self) -> None:
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_label.config(text="")
        self.status.config(text="Timer reset")

    # ---------- Quotes ----------
    def show_quote(self) -> None:
        if not self.quotes:
            return
        quote = random.choice(self.quotes)
        messagebox.showinfo("Quote", quote)

    # ---------- Hemingway mode ----------
    def toggle_hemingway(self) -> None:
        self.hemingway = not self.hemingway
        text = self._current_text()
        text.enable_hemingway(self.hemingway)
        state = "on" if self.hemingway else "off"
        self.status.config(text=f"Hemingway mode {state}")

    # ---------- Startup/shutdown ----------
    def _load_tabs(self) -> None:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    files = json.load(f)
            except Exception:
                files = []
        else:
            files = []
        for fname in files:
            path = os.path.join(DATA_DIR, fname)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.new_tab(fname, content)
        if not self.notebook.tabs():
            self.new_tab()

    def on_close(self) -> None:
        files = []
        for tab_id in self.notebook.tabs():
            frame = self.nametowidget(tab_id)
            text = frame.winfo_children()[0]
            if text.filename:
                files.append(text.filename)
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(files, f)
        self.destroy()


if __name__ == "__main__":
    app = GUINotator()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
