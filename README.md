# GUI Notator

A lightweight note-taking application written in Python using Tkinter. It provides
basic features such as multiple tabs, saving/loading notes, a countdown timer and a
quote viewer. It is designed to run on minimal hardware like a Raspberry Pi Zero 2 W.
Tabs and widgets use muted grays with a green accent for the cursor and active tab.

## Key Bindings

- `Ctrl+N` - New tab
- `Ctrl+O` - Open file
- `Ctrl+S` - Save
- `Ctrl+Shift+S` - Save As
- `Ctrl+W` - Close current tab
- `Ctrl+B` - Toggle tab bar
- `Ctrl+,` - Previous tab
- `Ctrl+.` - Next tab
- `Ctrl+L` - Show random quote
- `Ctrl+T` - Set timer
- `Ctrl+R` - Reset timer
- `Ctrl+G` - Toggle Hemingway mode
- `Ctrl+Delete` - Delete current file with haiku prompt

The **Save As** dialog suggests a timestamped `.md` filename. Deleting a note
requires typing a short haiku in an embedded panel. The prompts rotate through
lines borrowed from the original Textual version.

## Running

Make sure Tkinter is available. On Debian/Ubuntu you can install it with:

```bash
sudo apt-get install python3-tk
```

Then run the application with:

```bash
python3 main.py
```
