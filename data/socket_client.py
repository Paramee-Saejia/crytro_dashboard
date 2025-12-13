import json
import threading
import websocket
from queues.price_queue import price_queue


class BinancePriceSocket:
    def __init__(self, symbol):
        self.symbol = symbol.lower()

    def start(self):
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def _run(self):
        url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"

        ws = websocket.WebSocketApp(
            url,
            on_message=self._on_message
        )
        ws.run_forever()

    def _on_message(self, ws, msg):
        data = json.loads(msg)
        price = data.get("p")
        symbol = data.get("s")

        if price and symbol:
            price_queue.put((symbol, float(price)))
