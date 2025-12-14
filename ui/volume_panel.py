import tkinter as tk
from ui.stats_panel import StatBox


class VolumePanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#151823", padx=16, pady=16)

        self.buy_24h = StatBox(self, "Buy Volume (24H)", "-")
        self.buy_24h.pack(fill="x", pady=6)

        self.sell_24h = StatBox(self, "Sell Volume (24H)", "-")
        self.sell_24h.pack(fill="x", pady=6)

        self.ratio = StatBox(self, "Buy / Sell Ratio (24H)", "-")
        self.ratio.pack(fill="x", pady=6)

    def set_values(self, buy_text: str, sell_text: str, ratio_text: str):
        self.buy_24h.set_value(buy_text)
        self.sell_24h.set_value(sell_text)
        self.ratio.set_value(ratio_text)
