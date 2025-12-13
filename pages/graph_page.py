import tkinter as tk
import queue
import requests

from data.data_store import market_data
from queues.orderbook_queue import orderbook_queue
from data.socket_client import BinanceOrderBookSocket

from ui.header_panel import HeaderPanel
from ui.chart_panel import ChartPanel
from ui.stats_panel import StatsPanel
from ui.volume_panel import VolumePanel
from ui.orderbook_panel import OrderBookPanel


class GraphPage(tk.Frame):
    def __init__(self, parent, controller, symbol="BTCUSDT"):
        super().__init__(parent, bg="#0f111a")
        self.controller = controller

        self.symbol = symbol.upper()
        self.base, self.quote = self._split_symbol(self.symbol)

        self._last_price = None
        self._started_streams = set()

        self.header = HeaderPanel(self, on_back=lambda: self.controller.show_page("MainPage"))
        self.header.pack(fill="x", padx=24, pady=(16, 8))

        body = tk.Frame(self, bg="#0f111a")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=4, minsize=360)
        body.rowconfigure(1, weight=2)

        self.chart_panel = ChartPanel(body)
        self.chart_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12))

        self.stats_panel = StatsPanel(body)
        self.stats_panel.grid(row=0, column=1, sticky="nsew", pady=(0, 12))

        self.orderbook_panel = OrderBookPanel(body, rows=10)
        self.orderbook_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        self.volume_panel = VolumePanel(body)
        self.volume_panel.grid(row=1, column=1, sticky="nsew")

        self.set_symbol(self.symbol)

        self.after(200, self._refresh_header_price)
        self.after(100, self._poll_orderbook)
        self.after(2000, self._refresh_ticker_stats)


    def _split_symbol(self, symbol):
        s = symbol.upper()
        for q in ("USDT", "USDC", "BUSD"):
            if s.endswith(q):
                return s[:-len(q)], q
        return s, "USDT"

    def set_symbol(self, symbol):
        self.symbol = symbol.upper()
        self.base, self.quote = self._split_symbol(self.symbol)

        self.header.set_pair(self.base, self.quote)
        self.header.set_price("Loading...", color="white")

        self._last_price = None
        self._ensure_orderbook_stream()

    def _ensure_orderbook_stream(self):
        stream_symbol = self.symbol.lower()
        if stream_symbol in self._started_streams:
            return
        self._started_streams.add(stream_symbol)
        BinanceOrderBookSocket(stream_symbol, levels=10, interval_ms=100).start()

    def _refresh_header_price(self):
        price = market_data.prices.get(self.symbol)
        if price is not None:
            if self._last_price is None:
                color = "white"
                prefix = ""
            else:
                if price > self._last_price:
                    color = "#3ddc97"
                    prefix = "▲ "
                elif price < self._last_price:
                    color = "#ff5c5c"
                    prefix = "▼ "
                else:
                    color = "white"
                    prefix = ""

            self._last_price = price
            self.header.set_price(f"{prefix}{self.quote} {price:,.2f}", color=color)

        self.after(500, self._refresh_header_price)

    def _poll_orderbook(self):
        latest = None
        try:
            while True:
                sym, bids, asks = orderbook_queue.get_nowait()
                if sym == self.symbol:
                    latest = (bids, asks)
        except queue.Empty:
            pass

        if latest is not None:
            bids, asks = latest
            self.orderbook_panel.render(bids, asks)

        self.after(100, self._poll_orderbook)

    def _fmt_compact(self, x):
        try:
            x = float(x)
        except Exception:
            return "-"

        ax = abs(x)
        if ax >= 1_000_000_000:
            return f"{x/1_000_000_000:.2f}B"
        if ax >= 1_000_000:
            return f"{x/1_000_000:.2f}M"
        if ax >= 1_000:
            return f"{x/1_000:.2f}K"
        return f"{x:,.2f}"


    def _refresh_ticker_stats(self):
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={self.symbol}"

        try:
            r = requests.get(url, timeout=1.5)
            r.raise_for_status()
            data = r.json()

            change_pct = float(data.get("priceChangePercent", 0.0))
            high = data.get("highPrice")
            low = data.get("lowPrice")
            quote_vol = data.get("quoteVolume")

            change_text = f"{change_pct:+.2f}%"
            high_text = f"{self.quote} {float(high):,.2f}" if high is not None else "-"
            low_text = f"{self.quote} {float(low):,.2f}" if low is not None else "-"
            vol_text = f"{self._fmt_compact(quote_vol)} {self.quote}"

            self.stats_panel.set_ticker(change_text, high_text, low_text, vol_text)

        except Exception:
            self.stats_panel.set_ticker("-", "-", "-", "-")

        self.after(2000, self._refresh_ticker_stats)



