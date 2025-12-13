import json
import threading
import websocket
from queues.price_queue import price_queue


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
