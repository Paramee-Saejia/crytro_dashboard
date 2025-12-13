import json
import threading
import websocket
from queues.price_queue import price_queue
from queues.orderbook_queue import orderbook_queue


class BinancePriceSocket:
    def __init__(self, symbol: str):
        self.symbol = symbol.lower()

    def start(self):
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def _run(self):
        url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"
        ws = websocket.WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        ws.run_forever()

    def _on_open(self, ws):
        print("WS open:", self.symbol)

    def _on_error(self, ws, err):
        print("WS error:", self.symbol, err)

    def _on_close(self, ws, code, msg):
        print("WS close:", self.symbol, code, msg)

    def _on_message(self, ws, msg):
        data = json.loads(msg)
        sym = data.get("s")
        price = data.get("p")
        if sym and price:
            price_queue.put((sym, float(price)))


class BinanceOrderBookSocket:
    def __init__(self, symbol: str, levels: int = 10, interval_ms: int = 100):
        self.symbol_lc = symbol.lower()
        self.symbol_uc = symbol.upper()
        self.levels = levels
        self.interval_ms = interval_ms

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        url = f"wss://stream.binance.com:9443/ws/{self.symbol_lc}@depth{self.levels}@{self.interval_ms}ms"
        ws = websocket.WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        ws.run_forever(ping_interval=20, ping_timeout=10)

    def _on_open(self, ws):
        print("OB open:", self.symbol_lc)

    def _on_error(self, ws, err):
        print("OB error:", self.symbol_lc, err)

    def _on_close(self, ws, code, msg):
        print("OB close:", self.symbol_lc, code, msg)

    def _on_message(self, ws, msg):
        data = json.loads(msg)

        bids = data.get("b") or data.get("bids") or []
        asks = data.get("a") or data.get("asks") or []

        sym = data.get("s") or self.symbol_uc

        if bids or asks:
            orderbook_queue.put((sym, bids, asks))
