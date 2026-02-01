import tkinter as tk
from tkinter import font
from tkinter.scrolledtext import ScrolledText

class CaptionWindow:
    def __init__(self):
        # Window Setup
        self.root = tk.Tk()
        self.root.title("ADAM - Interface")
        self.root.geometry("600x500")
        self.root.configure(bg="#121212")
        self.root.attributes("-topmost", True)

        # Fonts
        self.font_chat = font.Font(family="Segoe UI", size=11)
        self.font_live = font.Font(family="Consolas", size=10, slant="italic")

        # --- LAYOUT FIX: Create Bottom Frame FIRST ---
        # We pack this to the BOTTOM so it reserves space immediately.
        self.bottom_frame = tk.Frame(self.root, bg="#121212")
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        # --- Live Captioning Area (Inside Bottom Frame) ---
        self.lbl_live_header = tk.Label(self.bottom_frame, text="LISTENING...", bg="#121212", fg="#666666", font=("Arial", 7, "bold"))
        self.lbl_live_header.pack(anchor="w")

        self.lbl_live = tk.Label(self.bottom_frame, text="Ready.", bg="#121212", fg="#888888",
                                 font=self.font_live, wraplength=580, justify="left", anchor="nw", height=2)
        self.lbl_live.pack(fill="x")

        # --- Chat History (Fills Remaining Space) ---
        self.chat_display = ScrolledText(self.root, bg="#1e1e1e", fg="#e0e0e0", 
                                         font=self.font_chat, wrap="word", borderwidth=0, padx=10, pady=10)
        # Pack to TOP and expand to fill whatever height is left
        self.chat_display.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        # Configure Color Tags
        self.chat_display.tag_config("user", foreground="#00ccff", spacing2=5)
        self.chat_display.tag_config("adam", foreground="#00ff00", spacing2=5)
        self.chat_display.tag_config("system", foreground="#888888", font=("Arial", 9, "italic"))
        
        self.chat_display.configure(state="disabled")

        # Force initial draw
        self.root.update()

    def _append_text(self, text, tag):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", text + "\n", tag)
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
        self.root.update()

    def update_live(self, text):
        display_text = text if text else "..."
        self.lbl_live.config(text=display_text, fg="white")
        self.root.update()

    def add_user_message(self, text):
        self._append_text(f"User: {text}", "user")
        self.lbl_live.config(text="Processing...", fg="gray")

    def add_ai_message(self, text):
        self._append_text(f"Adam: {text}\n", "adam")

    def add_system_log(self, text):
        self._append_text(f"[System]: {text}", "system")

    def close(self):
        self.root.destroy()