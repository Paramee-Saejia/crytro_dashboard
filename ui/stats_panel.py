import tkinter as tk


class StatBox(tk.Frame):
    def __init__(self, parent, title, value="-"):
        super().__init__(parent, bg="#1b1f2e", pady=8)

        tk.Label(
            self,
            text=title,
            fg="#9aa4c7",
            bg="#1b1f2e",
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        self.value_lbl = tk.Label(
            self,
            text=value,
            fg="white",
            bg="#1b1f2e",
            font=("Segoe UI", 12, "bold"),
        )
        self.value_lbl.pack(anchor="w")

    def set_value(self, value):
        self.value_lbl.config(text=value)


class StatsPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#151823", padx=16, pady=16)

        self.change_24h = StatBox(self, "24h Change", "-")
        self.change_24h.pack(fill="x", pady=6)

        self.high_24h = StatBox(self, "24h High", "-")
        self.high_24h.pack(fill="x", pady=6)

        self.low_24h = StatBox(self, "24h Low", "-")
        self.low_24h.pack(fill="x", pady=6)

        self.vol_24h = StatBox(self, "24h Volume (Quote)", "-")
        self.vol_24h.pack(fill="x", pady=6)

    def set_ticker(self, change_text, high_text, low_text, vol_text):
        self.change_24h.set_value(change_text)
        self.high_24h.set_value(high_text)
        self.low_24h.set_value(low_text)
        self.vol_24h.set_value(vol_text)

