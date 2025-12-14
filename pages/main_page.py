import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
from datetime import datetime

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
        super().__init__(parent, bg="#0f111a")
        self.controller = controller

        self._root_dir = Path(__file__).resolve().parents[1]
        self._icons = {}
        self._load_icons()

        self._last_price = {}
        self._last_update = {}

        self._build_ui()

        watchlist = self.controller.config.get(
            "watchlist",
            ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"],
        )
        self.rows = {}
        for sym in watchlist:
            self._add_row(sym.upper())

        self.after(500, self._refresh_updated_texts)
        self.refresh_prices()

    def _build_ui(self):
        top = tk.Frame(self, bg="#0f111a")
        top.pack(fill="x", padx=28, pady=(22, 14))

        tk.Label(
            top,
            text="ASSETS",
            bg="#0f111a",
            fg="#cbd5e1",
            font=("Segoe UI", 30, "bold"),
        ).pack(side="left")

        self.card = tk.Frame(self, bg="#151823")
        self.card.pack(fill="both", expand=True, padx=28, pady=(0, 24))

        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_rowconfigure(1, weight=1)

        header = tk.Frame(self.card, bg="#151823")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 10))

        cols = [
            ("Cryptocurrency", 0, "w"),
            ("Updated", 1, "w"),
            ("Change", 2, "w"),
            ("Price", 3, "e"),
            ("Volume 24h", 4, "e"),
            ("", 5, "e"),
        ]

        header.grid_columnconfigure(0, weight=3)
        header.grid_columnconfigure(1, weight=2)
        header.grid_columnconfigure(2, weight=2)
        header.grid_columnconfigure(3, weight=2)
        header.grid_columnconfigure(4, weight=2)
        header.grid_columnconfigure(5, weight=1)

        for text, c, anchor in cols:
            tk.Label(
                header,
                text=text,
                bg="#151823",
                fg="#9aa4c7",
                font=("Segoe UI", 10, "bold"),
            ).grid(row=0, column=c, sticky="ew", padx=8)

        tk.Frame(self.card, bg="#252a3d", height=1).grid(row=0, column=0, sticky="ew", padx=18, pady=(40, 0))

        self.table = tk.Frame(self.card, bg="#151823")
        self.table.grid(row=1, column=0, sticky="nsew", padx=18, pady=(10, 16))

        self.table.grid_columnconfigure(0, weight=3)
        self.table.grid_columnconfigure(1, weight=2)
        self.table.grid_columnconfigure(2, weight=2)
        self.table.grid_columnconfigure(3, weight=2)
        self.table.grid_columnconfigure(4, weight=2)
        self.table.grid_columnconfigure(5, weight=1)

        footer = tk.Frame(self.card, bg="#151823")
        footer.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 14))
        footer.grid_columnconfigure(0, weight=1)

        self.more_lbl = tk.Label(
            footer,
            text="More Assets",
            bg="#151823",
            fg="#7D67FF",
            font=("Segoe UI", 10, "underline"),
            cursor="hand2",
        )
        self.more_lbl.grid(row=0, column=0, sticky="e")

    def _load_icons(self):
        for sym, rel in CRYPTO_ICON_FILES.items():
            path = self._root_dir / rel
            if path.exists():
                img = Image.open(path).resize((28, 28), Image.LANCZOS)
                self._icons[sym] = ImageTk.PhotoImage(img, master=self)
            else:
                self._icons[sym] = None

    def _add_row(self, symbol):
        r = len(self.rows)

        row = tk.Frame(self.table, bg="#1b1f2e")
        row.grid(row=r, column=0, columnspan=6, sticky="ew", pady=8)

        inner = tk.Frame(row, bg="#1b1f2e", padx=14, pady=14)
        inner.pack(fill="x", expand=True)

        inner.grid_columnconfigure(0, weight=3)
        inner.grid_columnconfigure(1, weight=2)
        inner.grid_columnconfigure(2, weight=2)
        inner.grid_columnconfigure(3, weight=2)
        inner.grid_columnconfigure(4, weight=2)
        inner.grid_columnconfigure(5, weight=1)

        left = tk.Frame(inner, bg="#1b1f2e")
        left.grid(row=0, column=0, sticky="w", padx=8)

        icon = self._icons.get(symbol)
        if icon:
            lbl_icon = tk.Label(left, image=icon, bg="#1b1f2e")
            lbl_icon.image = icon
            lbl_icon.pack(side="left", padx=(0, 12))

        tk.Label(
            left,
            text=symbol,
            bg="#1b1f2e",
            fg="white",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")

        updated_lbl = tk.Label(
            inner,
            text="—",
            bg="#1b1f2e",
            fg="#9aa4c7",
            font=("Segoe UI", 11),
        )
        updated_lbl.grid(row=0, column=1, sticky="w", padx=8)

        change_lbl = tk.Label(
            inner,
            text="—",
            bg="#1b1f2e",
            fg="#9aa4c7",
            font=("Segoe UI", 11, "bold"),
        )
        change_lbl.grid(row=0, column=2, sticky="w", padx=8)

        price_lbl = tk.Label(
            inner,
            text="Loading...",
            bg="#1b1f2e",
            fg="white",
            font=("Segoe UI", 12, "bold"),
        )
        price_lbl.grid(row=0, column=3, sticky="e", padx=8)

        vol_lbl = tk.Label(
            inner,
            text="—",
            bg="#1b1f2e",
            fg="#9aa4c7",
            font=("Segoe UI", 11),
        )
        vol_lbl.grid(row=0, column=4, sticky="e", padx=8)

        btn = tk.Button(
            inner,
            text="View",
            command=lambda s=symbol: self._open_graph(s),
            bg="#0f111a",
            fg="white",
            activebackground="#0f111a",
            activeforeground="white",
            bd=0,
            padx=14,
            pady=6,
            font=("Segoe UI", 10, "bold"),
        )
        btn.grid(row=0, column=5, sticky="e", padx=6)

        self.rows[symbol] = {
            "price": price_lbl,
            "updated": updated_lbl,
            "change": change_lbl,
            "vol": vol_lbl,
        }

    def _open_graph(self, symbol):
        page = self.controller.pages.get("GraphPage")
        if page and hasattr(page, "set_symbol"):
            page.set_symbol(symbol)
        self.controller.show_page("GraphPage")

    def refresh_prices(self):
        for sym, widgets in self.rows.items():
            price = market_data.prices.get(sym)
            if price is not None:
                widgets["price"].config(text=f"{price:,.2f}")
                self._last_update[sym] = datetime.now()

    def update_price(self, symbol, price):
        symbol = symbol.upper()
        market_data.prices[symbol] = price

        widgets = self.rows.get(symbol)
        if not widgets:
            return

        prev = self._last_price.get(symbol)
        self._last_price[symbol] = price
        self._last_update[symbol] = datetime.now()

        widgets["price"].config(text=f"{price:,.2f}")

        if prev is None or prev == 0:
            widgets["change"].config(text="—", fg="#9aa4c7")
        else:
            pct = ((price - prev) / prev) * 100.0
            if pct > 0:
                widgets["change"].config(text=f"+{pct:.2f}%", fg="#3ddc97")
            elif pct < 0:
                widgets["change"].config(text=f"{pct:.2f}%", fg="#ff5c5c")
            else:
                widgets["change"].config(text="0.00%", fg="white")

        widgets["updated"].config(text="just now", fg="#9aa4c7")

    def update_24h(self, symbol, change_pct=None, volume_quote=None):
        symbol = symbol.upper()
        widgets = self.rows.get(symbol)
        if not widgets:
            return

        if change_pct is not None:
            if change_pct > 0:
                widgets["change"].config(text=f"+{change_pct:.2f}%", fg="#3ddc97")
            elif change_pct < 0:
                widgets["change"].config(text=f"{change_pct:.2f}%", fg="#ff5c5c")
            else:
                widgets["change"].config(text="0.00%", fg="white")

        if volume_quote is not None:
            widgets["vol"].config(text=volume_quote, fg="#9aa4c7")

    def _refresh_updated_texts(self):
        now = datetime.now()
        for sym, widgets in self.rows.items():
            t = self._last_update.get(sym)
            if not t:
                continue
            sec = int((now - t).total_seconds())
            if sec < 2:
                text = "just now"
            elif sec < 60:
                text = f"{sec}s ago"
            else:
                text = f"{sec // 60}m ago"
            widgets["updated"].config(text=text)

        self.after(500, self._refresh_updated_texts)
