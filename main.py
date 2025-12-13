import time
import queue

from data.socket_client import BinancePriceSocket
from queues.price_queue import price_queue

sock = BinancePriceSocket("btcusdt")
sock.start()

print("Socket running...")

while True:
    try:
        symbol, price = price_queue.get(timeout=1)
        print(symbol, price)
    except queue.Empty:
        pass





