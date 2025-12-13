import tkinter as tk
from ui.stats_panel import StatBox


class VolumePanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#151823", padx=16, pady=16)

        self.buy_1h = StatBox(self, "Buy Volume (1H)")
        self.buy_1h.pack(fill="x", pady=6)

        self.sell_1h = StatBox(self, "Sell Volume (1H)")
        self.sell_1h.pack(fill="x", pady=6)

        self.ratio = StatBox(self, "Buy / Sell Ratio")
        self.ratio.pack(fill="x", pady=6)
