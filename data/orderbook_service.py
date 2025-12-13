from data.socket_client import BinanceOrderBookSocket


class OrderBookService:
    def __init__(self, symbols):
        self.symbols = symbols
        self.sockets = []

    def start(self):
        for s in self.symbols:
            sock = BinanceOrderBookSocket(s, levels=10, interval_ms=100)
            sock.start()
            self.sockets.append(sock)
