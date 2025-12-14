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
        for sym in watchlist[:5]:
            self._add_row(sym.upper())

        self.after(500, self._refresh_updated_texts)
        self.refresh_prices()

    def _build_ui(self):
        top = tk.Frame(self, bg="#0f111a")
        top.pack(fill="x", padx=28, pady=(22, 10))

        tk.Label(
            top,
            text="ASSETS",
            bg="#0f111a",
            fg="#cbd5e1",
            font=("Segoe UI", 34, "bold"),
        ).pack(side="left")

        self.card = tk.Frame(self, bg="#151823")
        self.card.pack(fill="both", expand=True, padx=28, pady=(0, 18))

        self.table = tk.Frame(self.card, bg="#151823")
        self.table.pack(fill="both", expand=True, padx=18, pady=16)

        # 5 columns: crypto / updated / change / price / view
        # ให้ minsize ช่วยล็อคแนว ไม่ให้แกว่ง
        self.table.grid_columnconfigure(0, weight=4, minsize=360)
        self.table.grid_columnconfigure(1, weight=2, minsize=160)
        self.table.grid_columnconfigure(2, weight=2, minsize=160)
        self.table.grid_columnconfigure(3, weight=2, minsize=200)
        self.table.grid_columnconfigure(4, weight=1, minsize=120)

        # header (อยู่ใน grid เดียวกับ rows)
        headers = [
            ("Cryptocurrency", 0, "w"),
            ("Updated", 1, "w"),
            ("Change", 2, "w"),
            ("Price", 3, "e"),
            ("", 4, "e"),
        ]
        for text, c, stick in headers:
            tk.Label(
                self.table,
                text=text,
                bg="#151823",
                fg="#9aa4c7",
                font=("Segoe UI", 10, "bold"),
            ).grid(row=0, column=c, sticky=stick, padx=10, pady=(0, 12))

        tk.Frame(self.table, bg="#252a3d", height=1).grid(
            row=1, column=0, columnspan=5, sticky="ew", padx=6, pady=(0, 10)
        )

        self._next_row = 2

        # spacer ให้ card ดูเต็มจอ แต่ไม่ยืดแถวเพี้ยน
        self.table.grid_rowconfigure(999, weight=1)
        tk.Frame(self.table, bg="#151823").grid(row=999, column=0, columnspan=5, sticky="nsew")

    def _load_icons(self):
        for sym, rel in CRYPTO_ICON_FILES.items():
            path = self._root_dir / rel
            if path.exists():
                img = Image.open(path).resize((28, 28), Image.LANCZOS)
                self._icons[sym] = ImageTk.PhotoImage(img, master=self)
            else:
                self._icons[sym] = None

    def _cell(self, row, col, sticky="ew"):
        cell = tk.Frame(self.table, bg="#1b1f2e")
        cell.grid(row=row, column=col, sticky=sticky, padx=0, pady=10)
        return cell

    def _add_row(self, symbol):
        r = self._next_row
        self._next_row += 1

        # ----- Column 0: crypto (icon + text) -----
        c0 = self._cell(r, 0, sticky="ew")
        c0_in = tk.Frame(c0, bg="#1b1f2e")
        c0_in.pack(fill="x", expand=True, padx=16, pady=18)

        icon_box = tk.Frame(c0_in, bg="#1b1f2e", width=44, height=28)
        icon_box.pack(side="left")
        icon_box.pack_propagate(False)

        icon = self._icons.get(symbol)
        if icon:
            lbl_icon = tk.Label(icon_box, image=icon, bg="#1b1f2e")
            lbl_icon.image = icon
            lbl_icon.place(relx=0.0, rely=0.5, anchor="w")

        tk.Label(
            c0_in,
            text=symbol,
            bg="#1b1f2e",
            fg="white",
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left", padx=(10, 0))

        # ----- Column 1: updated -----
        c1 = self._cell(r, 1, sticky="ew")
        updated_lbl = tk.Label(
            c1,
            text="—",
            bg="#1b1f2e",
            fg="#9aa4c7",
            font=("Segoe UI", 11),
        )
        updated_lbl.pack(anchor="w", padx=16, pady=18)

        # ----- Column 2: change -----
        c2 = self._cell(r, 2, sticky="ew")
        change_lbl = tk.Label(
            c2,
            text="—",
            bg="#1b1f2e",
            fg="#9aa4c7",
            font=("Segoe UI", 11, "bold"),
        )
        change_lbl.pack(anchor="w", padx=16, pady=18)

        # ----- Column 3: price (right align) -----
        c3 = self._cell(r, 3, sticky="ew")
        price_lbl = tk.Label(
            c3,
            text="Loading...",
            bg="#1b1f2e",
            fg="white",
            font=("Segoe UI", 12, "bold"),
        )
        price_lbl.pack(anchor="e", padx=16, pady=18)

        # ----- Column 4: view button (right align) -----
        c4 = self._cell(r, 4, sticky="ew")
        btn = tk.Button(
            c4,
            text="View",
            command=lambda s=symbol: self._open_graph(s),
            bg="#0f111a",
            fg="white",
            activebackground="#0f111a",
            activeforeground="white",
            bd=0,
            padx=16,
            pady=8,
            font=("Segoe UI", 10, "bold"),
        )
        btn.pack(anchor="e", padx=16, pady=16)

        self.rows[symbol] = {
            "price": price_lbl,
            "updated": updated_lbl,
            "change": change_lbl,
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
