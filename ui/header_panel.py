import tkinter as tk


class HeaderPanel(tk.Frame):
    def __init__(self, parent, on_back):
        super().__init__(parent, bg="#0f111a", height=60)

        self.back_btn = tk.Button(
            self,
            text="←",
            font=("Segoe UI", 14),
            fg="white",
            bg="#0f111a",
            bd=0,
            activebackground="#0f111a",
            activeforeground="white",
            command=on_back,
            cursor="hand2",
        )
        self.back_btn.pack(side="left")

        self.title_lbl = tk.Label(
            self,
            text="",
            fg="white",
            bg="#0f111a",
            font=("Segoe UI", 18, "bold"),
        )
        self.title_lbl.pack(side="left", padx=12)

        self.price_lbl = tk.Label(
            self,
            text="",
            fg="white",
            bg="#0f111a",
            font=("Segoe UI", 16, "bold"),
        )
        self.price_lbl.pack(side="right")

    def set_pair(self, base, quote):
        self.title_lbl.config(text=f"{base} / {quote}")

    def set_price(self, text, color="white"):
        self.price_lbl.config(text=text, fg=color)
