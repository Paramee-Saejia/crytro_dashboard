import json
import websocket

URL = "wss://stream.binance.com:9443/ws/btcusdt@depth10@100ms"

def on_open(ws):
    print("OPEN")

def on_error(ws, err):
    print("ERROR:", err)

def on_close(ws, code, msg):
    print("CLOSE:", code, msg)

def on_message(ws, msg):
    data = json.loads(msg)

    bids = data.get("bids") or data.get("b") or []
    asks = data.get("asks") or data.get("a") or []

    print("MSG:", "BTCUSDT", len(bids), len(asks))
    if bids:
        print("TOP BID:", bids[0])
    if asks:
        print("TOP ASK:", asks[0])

    ws.close()

ws = websocket.WebSocketApp(
    URL,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)

ws.run_forever(ping_interval=20, ping_timeout=10)
