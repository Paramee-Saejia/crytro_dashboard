import tkinter as tk
import queue
import requests

from data.data_store import market_data
from queues.orderbook_queue import orderbook_queue
from data.socket_client import BinanceOrderBookSocket

from ui.header_panel import HeaderPanel
from ui.candlestick_chart import CandlestickChart
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
        self._ob_sockets = {}  # symbol_lc -> BinanceOrderBookSocket

        self.header = HeaderPanel(self, on_back=lambda: self.controller.show_page("MainPage"))
        self.header.pack(fill="x", padx=24, pady=(16, 8))

        # toggle buttons row (ใต้ header นิดเดียว)
        self.toggle_bar = tk.Frame(self, bg="#0f111a")
        self.toggle_bar.pack(fill="x", padx=24, pady=(0, 8))

        self._btn_stats = tk.Button(self.toggle_bar, text="Stats", command=lambda: self._toggle_panel("stats"))
        self._btn_ob = tk.Button(self.toggle_bar, text="Order Book", command=lambda: self._toggle_panel("orderbook"))
        self._btn_vol = tk.Button(self.toggle_bar, text="Volume", command=lambda: self._toggle_panel("volume"))

        for b in (self._btn_stats, self._btn_ob, self._btn_vol):
            b.configure(
                bg="#151823", fg="white", bd=0,
                activebackground="#1b1f2e", activeforeground="white",
                padx=14, pady=6, font=("Segoe UI", 10, "bold"),
                cursor="hand2",
            )
            b.pack(side="left", padx=(0, 10))

        body = tk.Frame(self, bg="#0f111a")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=4, minsize=360)
        body.rowconfigure(1, weight=2)

        self.chart_panel = CandlestickChart(body, on_hover=self._on_chart_hover)
        self.chart_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12))

        self.stats_panel = StatsPanel(body)
        self.stats_panel.grid(row=0, column=1, sticky="nsew", pady=(0, 12))

        self.orderbook_panel = OrderBookPanel(body, rows=10)
        self.orderbook_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        self.volume_panel = VolumePanel(body)
        self.volume_panel.grid(row=1, column=1, sticky="nsew")

        # apply saved panel visibility
        self._apply_panel_visibility_from_settings()

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

    # ---------------- toggles ----------------
    def _get_panels_cfg(self):
        cfg = self.controller.app_config.setdefault("panels", {"stats": True, "orderbook": True, "volume": True})
        cfg.setdefault("stats", True)
        cfg.setdefault("orderbook", True)
        cfg.setdefault("volume", True)
        return cfg

    def _apply_panel_visibility_from_settings(self):
        cfg = self._get_panels_cfg()
        self._set_panel_visible("stats", cfg.get("stats", True))
        self._set_panel_visible("orderbook", cfg.get("orderbook", True))
        self._set_panel_visible("volume", cfg.get("volume", True))
        self._update_toggle_button_styles()

    def _set_panel_visible(self, name, visible: bool):
        if name == "stats":
            w = self.stats_panel
        elif name == "orderbook":
            w = self.orderbook_panel
        elif name == "volume":
            w = self.volume_panel
        else:
            return

        if visible:
            w.grid()
        else:
            w.grid_remove()

    def _toggle_panel(self, name):
        cfg = self._get_panels_cfg()
        cfg[name] = not bool(cfg.get(name, True))
        self._set_panel_visible(name, cfg[name])
        self._update_toggle_button_styles()

        # save immediately (กันไฟดับ/ปิดแอป)
        try:
            self.controller.settings_store.data = self.controller.app_config
            self.controller.settings_store.save()
        except Exception:
            pass

    def _update_toggle_button_styles(self):
        cfg = self._get_panels_cfg()

        def style(btn, on):
            btn.configure(bg="#1b1f2e" if on else "#151823", fg="white")

        style(self._btn_stats, cfg.get("stats", True))
        style(self._btn_ob, cfg.get("orderbook", True))
        style(self._btn_vol, cfg.get("volume", True))

    # ---------------- symbol & streams ----------------
    def set_symbol(self, symbol):
        self.symbol = symbol.upper()
        self.base, self.quote = self._split_symbol(self.symbol)

        self.header.set_pair(self.base, self.quote)
        self.header.set_price("Loading...", color="white")
        self.chart_panel.set_symbol(self.symbol, interval="1m")

        self._last_price = None
        self._ensure_orderbook_stream()

    def _ensure_orderbook_stream(self):
        stream_symbol = self.symbol.lower()
        if stream_symbol in self._ob_sockets:
            return

        sock = BinanceOrderBookSocket(stream_symbol, levels=10, interval_ms=100)
        sock.start()
        self._ob_sockets[stream_symbol] = sock

    # ให้ App เรียกอัปเดตราคาแบบ realtime (ไม่ต้องรอ refresh)
    def on_price(self, symbol, price):
        if symbol.upper() != self.symbol:
            return
        market_data.prices[self.symbol] = price

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

    def _on_chart_hover(self, close_price: float, pct: float):
        if close_price is None:
            return

        color = "#3ddc97" if pct > 0 else "#ff5c5c" if pct < 0 else "white"
        sign_pct = f"{pct:+.2f}%"
        # HeaderPanel ของคุณใช้ set_price() ไม่ใช่ set_price_text()
        self.header.set_price(f"{self.quote} {close_price:,.2f}  ({sign_pct})", color=color)

    def on_close(self):
        # stop orderbook sockets started by this page
        for s in list(self._ob_sockets.values()):
            if hasattr(s, "stop"):
                try:
                    s.stop()
                except Exception:
                    pass
        self._ob_sockets.clear()
