import json
import threading
import websocket

from queues.price_queue import price_queue
from queues.orderbook_queue import orderbook_queue


class BinancePriceSocket:
    def __init__(self, symbol: str):
        self.symbol = symbol.lower()
        self._ws = None
        self._thread = None
        self._stop = threading.Event()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        try:
            if self._ws is not None:
                self._ws.close()
        except Exception:
            pass

    def _run(self):
        url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"

        ws = websocket.WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self._ws = ws

        # loop แบบสั้น ๆ เพื่อให้ stop ได้
        while not self._stop.is_set():
            try:
                ws.run_forever(ping_interval=20, ping_timeout=10)
            except Exception:
                pass
            if not self._stop.is_set():
                # ถ้าหลุดเอง ให้ต่อใหม่
                continue
            break

    def _on_open(self, ws):
        # print("WS open:", self.symbol)
        pass

    def _on_error(self, ws, err):
        if not self._stop.is_set():
            print("WS error:", self.symbol, err)

    def _on_close(self, ws, code, msg):
        # print("WS close:", self.symbol, code, msg)
        pass

    def _on_message(self, ws, msg):
        if self._stop.is_set():
            return

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

        self._ws = None
        self._thread = None
        self._stop = threading.Event()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        try:
            if self._ws is not None:
                self._ws.close()
        except Exception:
            pass

    def _run(self):
        url = f"wss://stream.binance.com:9443/ws/{self.symbol_lc}@depth{self.levels}@{self.interval_ms}ms"

        ws = websocket.WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self._ws = ws

        while not self._stop.is_set():
            try:
                ws.run_forever(ping_interval=20, ping_timeout=10)
            except Exception:
                pass
            if not self._stop.is_set():
                continue
            break

    def _on_open(self, ws):
        # print("OB open:", self.symbol_lc)
        pass

    def _on_error(self, ws, err):
        if not self._stop.is_set():
            print("OB error:", self.symbol_lc, err)

    def _on_close(self, ws, code, msg):
        # print("OB close:", self.symbol_lc, code, msg)
        pass

    def _on_message(self, ws, msg):
        if self._stop.is_set():
            return

        data = json.loads(msg)
        bids = data.get("b") or data.get("bids") or []
        asks = data.get("a") or data.get("asks") or []
        sym = data.get("s") or self.symbol_uc

        if bids or asks:
            orderbook_queue.put((sym, bids, asks))
