import random
import tkinter as tk
from pathlib import Path
import sys
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont

SECRET_CODE = "67"
MAX_WINDOWS = 1000
INTERVAL_MS = 500
IMAGE_SIZE = (440, 340)

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

MEMES_DIR = BASE_DIR / "memes"

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".jfif", ".png", ".gif", ".webp"
}

# Кольорова гама
C_BG = "#090d16"
C_SURFACE = "#131b2e"
C_SURFACE_HOVER = "#1c2640"
C_BORDER = "#1e293b"
C_BORDER_FOCUS = "#38bdf8"

C_PRIMARY = "#f43f5e"
C_PRIMARY_HOVER = "#e11d48"
C_PURPLE = "#8b5cf6"
C_PURPLE_HOVER = "#7c3aed"

C_TEXT_MAIN = "#f8fafc"
C_TEXT_MUTED = "#64748b"
C_TEXT_SUB = "#94a3b8"

BG_OLD = "#17152b"
ACCENTS = ["#ff4d8d", "#8b5cf6", "#06b6d4", "#f59e0b", "#22c55e"]

windows = []
created = 0
stopped = False


def find_memes():
    if not MEMES_DIR.is_dir():
        return []

    return sorted(
        [
            p for p in MEMES_DIR.iterdir()
            if p.is_file()
            and p.suffix.lower() in IMAGE_EXTENSIONS
        ]
    )


def close_one(win):
    if win in windows:
        windows.remove(win)

    try:
        win.destroy()
    except tk.TclError:
        pass


def stop_demo():
    global stopped
    stopped = True

    for win in windows[:]:
        close_one(win)

    windows.clear()

    status_dot.config(fg="#38bdf8")
    status_text.config(
        text="Зупинено",
        fg="#38bdf8"
    )

    btn_close.pack(fill="x", pady=(0, 10))


def close_app():
    if stopped:
        root.destroy()


def check_code(event=None):
    entered = code_entry.get().strip().upper()

    if entered == SECRET_CODE:
        code_entry.delete(0, tk.END)
        stop_demo()
    else:
        status_dot.config(fg="#f43f5e")
        status_text.config(
            text="Невірний код!",
            fg="#f43f5e"
        )
        code_entry.delete(0, tk.END)


def add_hidden_code(img, count):
    if count == 0 or (count + 1) % 30 != 0:
        return img

    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 9)
    except OSError:
        font = ImageFont.load_default()

    text = SECRET_CODE
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    corners = [
        (3, 3),
        (max(3, img.width - text_width - 3), 3),
        (3, max(3, img.height - text_height - 3)),
        (
            max(3, img.width - text_width - 3),
            max(3, img.height - text_height - 3)
        ),
    ]

    x, y = random.choice(corners)

    draw.text(
        (x, y),
        text,
        font=font,
        fill=(145, 145, 145)
    )

    return img


def show_meme():
    global created

    if stopped or not root.winfo_exists():
        return

    paths = find_memes()

    if not paths:
        status_dot.config(fg="#f43f5e")
        status_text.config(
            text="Папка memes порожня",
            fg="#f43f5e"
        )
        return

    if len(windows) >= MAX_WINDOWS:
        status_dot.config(fg="#f59e0b")
        status_text.config(
            text="Ліміт вікон! Введи код",
            fg="#f59e0b"
        )
        return

    random.shuffle(paths)
    photo = None

    for path in paths:
        try:
            with Image.open(path) as source:
                img = ImageOps.exif_transpose(source).convert("RGB")
                img.thumbnail(IMAGE_SIZE)
                img = add_hidden_code(img, created)
                photo = ImageTk.PhotoImage(img)
            break

        except Exception as exc:
            print(f"Помилка {path.name}: {exc}")

    if photo is None:
        status_dot.config(fg="#f43f5e")
        status_text.config(
            text="Помилка зчитування файлу",
            fg="#f43f5e"
        )
        return

    accent = random.choice(ACCENTS)

    win = tk.Toplevel(root)
    win.title(f"MemeStorm #{created + 1}")
    win.configure(bg=accent)
    win.resizable(False, False)
    
    win.attributes("-topmost", True)

    image_label = tk.Label(
        win,
        image=photo,
        bg=BG_OLD,
        padx=2,
        pady=2
    )
    image_label.image = photo
    image_label.pack(padx=4, pady=4)

    win.protocol("WM_DELETE_WINDOW", lambda: None)
    win.update_idletasks()

    window_width = win.winfo_width()
    window_height = win.winfo_height()

    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    x = random.randint(0, max(0, screen_width - window_width))
    y = random.randint(0, max(0, screen_height - window_height))

    win.geometry(f"+{x}+{y}")
    win.lift()

    windows.append(win)
    created += 1

    status_dot.config(fg="#10b981")
    status_text.config(
        text="Спам запущено",
        fg="#10b981"
    )

    root.after(INTERVAL_MS, show_meme)


# Головне вікно
root = tk.Tk()
root.title("MemeStorm")
root.geometry("400x460")
root.configure(bg=C_BG)
root.resizable(False, False)

root.attributes("-topmost", True)
root.protocol("WM_DELETE_WINDOW", lambda: None)

# Функція для постійної підтримки головного вікна поверх усіх мемів
def keep_root_on_top():
    if not stopped and root.winfo_exists():
        root.lift()
        root.attributes("-topmost", True)
        root.after(200, keep_root_on_top)

# Інтерфейс головного вікна
main = tk.Frame(root, bg=C_BG)
main.pack(fill="both", expand=True, padx=28, pady=24)

# Хедер
header_frame = tk.Frame(main, bg=C_BG)
header_frame.pack(fill="x", pady=(0, 20))

tk.Label(
    header_frame,
    text="MemeStorm",
    font=("Segoe UI", 30, "bold"),
    bg=C_BG,
    fg=C_TEXT_MAIN,
    anchor="center"
).pack(fill="x")

tk.Label(
    header_frame,
    text="Система заповнення робочого столу",
    font=("Segoe UI", 10),
    bg=C_BG,
    fg=C_TEXT_MUTED,
    anchor="center"
).pack(fill="x", pady=(4, 0))

# Картка поля вводу
entry_card = tk.Frame(
    main,
    bg=C_SURFACE,
    padx=16,
    pady=14,
    highlightbackground=C_BORDER,
    highlightthickness=1
)
entry_card.pack(fill="x", pady=(0, 16))

tk.Label(
    entry_card,
    text="СЕКРЕТНИЙ КОД ЗУПИНКИ",
    font=("Segoe UI", 8, "bold"),
    bg=C_SURFACE,
    fg=C_TEXT_MUTED
).pack(anchor="w", pady=(0, 8))

entry_wrapper = tk.Frame(
    entry_card,
    bg=C_BG,
    highlightbackground=C_BORDER,
    highlightthickness=1
)
entry_wrapper.pack(fill="x")

code_entry = tk.Entry(
    entry_wrapper,
    show="•",
    font=("Consolas", 13, "bold"),
    justify="center",
    bg=C_BG,
    fg=C_PRIMARY,
    insertbackground=C_PRIMARY,
    bd=0,
    relief="flat"
)
code_entry.pack(fill="x", ipady=8, padx=8)
code_entry.bind("<Return>", check_code)

def on_focus_in(e):
    entry_wrapper.config(highlightbackground=C_BORDER_FOCUS)

def on_focus_out(e):
    entry_wrapper.config(highlightbackground=C_BORDER)

code_entry.bind("<FocusIn>", on_focus_in)
code_entry.bind("<FocusOut>", on_focus_out)

# Кнопка зупинки
btn_stop = tk.Label(
    main,
    text="ЗУПИНИТИ АТАКУ",
    font=("Segoe UI", 10, "bold"),
    bg=C_PURPLE,
    fg=C_TEXT_MAIN,
    pady=11,
    cursor="hand2"
)
btn_stop.pack(fill="x", pady=(0, 10))

btn_stop.bind("<Enter>", lambda e: btn_stop.configure(bg=C_PURPLE_HOVER))
btn_stop.bind("<Leave>", lambda e: btn_stop.configure(bg=C_PURPLE))
btn_stop.bind("<Button-1>", lambda e: check_code())

# Кнопка закриття — спочатку прихована
btn_close = tk.Label(
    main,
    text="ЗАКРИТИ ПРОГРАМУ",
    font=("Segoe UI", 10, "bold"),
    bg=C_PURPLE,
    fg=C_TEXT_MAIN,
    pady=11,
    cursor="hand2"
)

btn_close.bind("<Enter>", lambda e: btn_close.configure(bg=C_PURPLE_HOVER))
btn_close.bind("<Leave>", lambda e: btn_close.configure(bg=C_PURPLE))
btn_close.bind("<Button-1>", lambda e: close_app())

# Футер та статус
status_frame = tk.Frame(main, bg=C_BG)
status_frame.pack(side="bottom", fill="x")

status_dot = tk.Label(
    status_frame,
    text="●",
    font=("Segoe UI", 8),
    bg=C_BG,
    fg="#10b981"
)
status_dot.pack(side="left", padx=(0, 6))

status_text = tk.Label(
    status_frame,
    text="Очікування запуску...",
    font=("Segoe UI", 9),
    bg=C_BG,
    fg=C_TEXT_MUTED
)
status_text.pack(side="left")

# Запуск таймерів та головного циклу програми
root.after(500, show_meme)
root.after(200, keep_root_on_top)
root.mainloop()