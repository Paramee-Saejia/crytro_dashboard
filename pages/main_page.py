import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk

from data.data_store import market_data


CRYPTO_ICON_FILES = {
    "BTCUSDT": r"images\icon_Cryptro\bitcoin.png",
    "ETHUSDT": r"images\icon_Cryptro\eth.png",
    "SOLUSDT": r"images\icon_Cryptro\sol.png",
    "BNBUSDT": r"images\icon_Cryptro\bnb.png",
    "XRPUSDT": r"images\icon_Cryptro\xrp.png",
}


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1b1b2f")
        self.controller = controller

        self._root_dir = Path(__file__).resolve().parents[1]
        self._icons = {}
        self._load_icons()

        tk.Label(
            self,
            text="Main Page",
            bg="#1b1b2f",
            fg="white",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(16, 10))

        self.rows = {}

        watchlist = self.controller.config.get(
            "watchlist",
            ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"],
        )

        for sym in watchlist:
            self._add_row(sym.upper())

        self.refresh_prices()

    def _load_icons(self):
        for sym, rel in CRYPTO_ICON_FILES.items():
            path = self._root_dir / rel
            if path.exists():
                img = Image.open(path).resize((28, 28), Image.LANCZOS)
                self._icons[sym] = ImageTk.PhotoImage(img, master=self)
            else:
                self._icons[sym] = None

    def _add_row(self, symbol):
        row = tk.Frame(self, bg="#2a2a40", padx=12, pady=10)
        row.pack(fill="x", padx=20, pady=8)

        icon = self._icons.get(symbol)
        if icon:
            lbl_icon = tk.Label(row, image=icon, bg="#2a2a40")
            lbl_icon.image = icon
            lbl_icon.pack(side="left", padx=(0, 10))

        tk.Label(
            row,
            text=symbol,
            bg="#2a2a40",
            fg="white",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")

        btn = tk.Button(
            row,
            text="View",
            command=lambda s=symbol: self._open_graph(s),
        )
        btn.pack(side="right")

        price_lbl = tk.Label(
            row,
            text="Loading...",
            bg="#2a2a40",
            fg="white",
            font=("Segoe UI", 12),
        )
        price_lbl.pack(side="right", padx=(10, 0))

        self.rows[symbol] = price_lbl

    def _open_graph(self, symbol):
        page = self.controller.pages.get("GraphPage")
        if page and hasattr(page, "set_symbol"):
            page.set_symbol(symbol)
        self.controller.show_page("GraphPage")

    def refresh_prices(self):
        for sym, lbl in self.rows.items():
            price = market_data.prices.get(sym)
            if price is not None:
                lbl.config(text=f"{price:,.2f}")

    def update_price(self, symbol, price):
        symbol = symbol.upper()
        market_data.prices[symbol] = price
        lbl = self.rows.get(symbol)
        if lbl is not None:
            lbl.config(text=f"{price:,.2f}")
