import tkinter as tk
import queue
from queues.orderbook_queue import orderbook_queue
from data.socket_client import BinanceOrderBookSocket



class HeaderPanel(tk.Frame):
    def __init__(self, parent, on_back):
        super().__init__(parent, bg="#0f111a", height=60)
        self._on_back = on_back

        self.back_btn = tk.Button(
            self,
            text="←",
            font=("Segoe UI", 14),
            fg="white",
            bg="#0f111a",
            bd=0,
            activebackground="#0f111a",
            command=self._on_back
        )
        self.back_btn.pack(side="left")

        self.title_lbl = tk.Label(
            self,
            text="",
            fg="white",
            bg="#0f111a",
            font=("Segoe UI", 18, "bold")
        )
        self.title_lbl.pack(side="left", padx=12)

        self.price_lbl = tk.Label(
            self,
            text="",
            fg="#ff5c5c",
            bg="#0f111a",
            font=("Segoe UI", 16, "bold")
        )
        self.price_lbl.pack(side="right")




    def set_title(self, symbol):
        self.title_lbl.config(text=f"{symbol} / THB")

    def set_price_text(self, text, color=None):
        if color:
            self.price_lbl.config(fg=color)
        self.price_lbl.config(text=text)


class StatBox(tk.Frame):
    def __init__(self, parent, title, value):
        super().__init__(parent, bg="#1b1f2e", pady=8)

        self.title_lbl = tk.Label(
            self,
            text=title,
            fg="#9aa4c7",
            bg="#1b1f2e",
            font=("Segoe UI", 9)
        )
        self.title_lbl.pack(anchor="w")

        self.value_lbl = tk.Label(
            self,
            text=value,
            fg="white",
            bg="#1b1f2e",
            font=("Segoe UI", 12, "bold")
        )
        self.value_lbl.pack(anchor="w")

    def set_value(self, value):
        self.value_lbl.config(text=value)


class StatsPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#151823", padx=16, pady=16)

        self.market_cap = StatBox(self, "Market Cap", "-")
        self.market_cap.pack(fill="x", pady=6)

        self.vol_24h = StatBox(self, "24h Volume", "-")
        self.vol_24h.pack(fill="x", pady=6)

        self.supply = StatBox(self, "Circulating Supply", "-")
        self.supply.pack(fill="x", pady=6)


class VolumePanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#151823", padx=16, pady=16)

        self.buy_1h = StatBox(self, "Buy Volume (1H)", "-")
        self.buy_1h.pack(fill="x", pady=6)

        self.sell_1h = StatBox(self, "Sell Volume (1H)", "-")
        self.sell_1h.pack(fill="x", pady=6)

        self.ratio = StatBox(self, "Buy / Sell Ratio", "-")
        self.ratio.pack(fill="x", pady=6)


class ChartPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#151823", padx=16, pady=16)

        tk.Label(
            self,
            text="Price Chart (1D)",
            fg="white",
            bg="#151823",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        self.canvas = tk.Canvas(self, bg="#1b1f2e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, pady=12)

        self._draw_placeholder()

    def _draw_placeholder(self):
        self.canvas.create_line(
            20, 120, 80, 90, 140, 130, 200, 80,
            260, 100, 320, 70, 380, 110,
            smooth=True,
            fill="#4da3ff",
            width=2
        )


class OrderBookPanel(tk.Frame):
    def __init__(self, parent, rows=10):
        super().__init__(parent, bg="#151823", padx=16, pady=16)
        self.rows = rows

        tk.Label(
            self,
            text="Order Book",
            fg="white",
            bg="#151823",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))

        table = tk.Frame(self, bg="#151823")
        table.pack(fill="both", expand=True)

        self.ask_labels = []
        self.bid_labels = []

        tk.Label(table, text="ASK", fg="#ff5c5c", bg="#151823",
                 font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=8, pady=(0, 6))
        tk.Label(table, text="BID", fg="#3ddc97", bg="#151823",
                 font=("Segoe UI", 11, "bold")).grid(row=0, column=1, sticky="w", padx=8, pady=(0, 6))

        for i in range(self.rows):
            a = tk.Label(table, text="", fg="white", bg="#151823", font=("Segoe UI", 10))
            b = tk.Label(table, text="", fg="white", bg="#151823", font=("Segoe UI", 10))
            a.grid(row=i + 1, column=0, sticky="w", padx=8, pady=2)
            b.grid(row=i + 1, column=1, sticky="w", padx=8, pady=2)
            self.ask_labels.append(a)
            self.bid_labels.append(b)

    def render(self, bids, asks):
        asks_view = asks[: self.rows]
        bids_view = bids[: self.rows]

        for i in range(self.rows):
            if i < len(asks_view):
                p, q = asks_view[i]
                self.ask_labels[i].config(text=f"{p} | {q}", fg="#ff5c5c")
            else:
                self.ask_labels[i].config(text="")

            if i < len(bids_view):
                p, q = bids_view[i]
                self.bid_labels[i].config(text=f"{p} | {q}", fg="#3ddc97")
            else:
                self.bid_labels[i].config(text="")


class GraphPage(tk.Frame):
    def __init__(self, parent, controller, symbol="BTCUSDT"):
        super().__init__(parent, bg="#0f111a")
        self.controller = controller
        self.symbol = symbol

        self.header = HeaderPanel(self, on_back=lambda: self.controller.show_page("MainPage"))
        self.header.pack(fill="x", padx=24, pady=(16, 8))

        body = tk.Frame(self, bg="#0f111a")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=3)
        body.rowconfigure(1, weight=2)

        self.chart_panel = ChartPanel(body)
        self.chart_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12))

        self.stats_panel = StatsPanel(body)
        self.stats_panel.grid(row=0, column=1, sticky="nsew", pady=(0, 12))

        self.orderbook_panel = OrderBookPanel(body, rows=10)
        self.orderbook_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        self.volume_panel = VolumePanel(body)
        self.volume_panel.grid(row=1, column=1, sticky="nsew")

        self._ob_socket = None
        self.after(100, self._poll_orderbook)
        self.set_symbol(self.symbol)


        self.set_symbol(self.symbol)
        
        self._ob_socket = None
        self.after(100, self._poll_orderbook)

        self._ob_socket = None
        self.after(100, self._poll_orderbook)
        self.set_symbol(self.symbol)


    def set_symbol(self, symbol):
        self.symbol = symbol.upper() 
        self.header.set_title(self.symbol)
        self.header.set_price_text("Loading...", color="white")
        self._start_orderbook_stream()


    def set_price(self, price_text, updown_color=None):
        self.header.set_price_text(price_text, color=updown_color)

    def render_orderbook(self, bids, asks):
        self.orderbook_panel.render(bids, asks)

    def _start_orderbook_stream(self):
        # symbol send to binance in lower case
        stream_symbol = self.symbol.lower()
        print("Start OB stream:", stream_symbol)
        # draft ver
        self._ob_socket = BinanceOrderBookSocket(stream_symbol, levels=10, interval_ms=100)
        self._ob_socket.start()

    def _poll_orderbook(self):
        try:
            while True:
                sym, bids, asks = orderbook_queue.get_nowait()
                if sym == self.symbol:
                    self.orderbook_panel.render(bids, asks)
        except queue.Empty:
            pass

        self.after(100, self._poll_orderbook)

    def update_orderbook(self, symbol, bids, asks):
        if symbol == self.symbol:
            self.orderbook_panel.render(bids, asks)



