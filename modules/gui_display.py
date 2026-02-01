import tkinter as tk
from tkinter import font

class CaptionWindow:
    def __init__(self):
        # Window Setup
        self.root = tk.Tk()
        self.root.title("ADAM - Live Interface")
        self.root.geometry("500x300")
        self.root.configure(bg="#121212")
        self.root.attributes("-topmost", True) # Keep window on top of others

        # Fonts
        self.font_live = font.Font(family="Segoe UI", size=14)
        self.font_context = font.Font(family="Consolas", size=10)

        # --- Section 1: Live Captioning ---
        self.lbl_live_header = tk.Label(self.root, text="LIVE INPUT (Whisper)", bg="#121212", fg="#00ff00", font=("Arial", 8, "bold"))
        self.lbl_live_header.pack(anchor="w", padx=10, pady=(10, 0))

        self.lbl_live = tk.Label(self.root, text="Listening...", bg="#1e1e1e", fg="white",
                                 font=self.font_live, wraplength=480, justify="left", anchor="nw", height=4)
        self.lbl_live.pack(fill="x", padx=10, pady=5)

        # --- Section 2: User Context (Final Output) ---
        self.lbl_ctx_header = tk.Label(self.root, text="COMMITTED CONTEXT", bg="#121212", fg="#00ccff", font=("Arial", 8, "bold"))
        self.lbl_ctx_header.pack(anchor="w", padx=10, pady=(10, 0))

        self.lbl_context = tk.Label(self.root, text="...", bg="#1e1e1e", fg="#aaaaaa",
                                    font=self.font_context, wraplength=480, justify="left", anchor="nw", height=6)
        self.lbl_context.pack(fill="both", expand=True, padx=10, pady=5)

        # Force initial draw
        self.root.update()

    def update_live(self, text):
        """Updates the streaming text and refreshes the GUI."""
        display_text = text if text else "..."
        self.lbl_live.config(text=display_text, fg="white")
        # CRITICAL: This keeps the window responsive while the main loop waits for voice
        self.root.update()

    def update_context(self, text):
        """Updates the final text after processing."""
        self.lbl_context.config(text=text, fg="#00ccff")
        self.lbl_live.config(text="Processing...", fg="gray")
        self.root.update()

    def close(self):
        self.root.destroy()