from data.socket_client import BinancePriceSocket


class PriceService:
    def __init__(self, symbols):
        self.symbols = symbols
        self.sockets = []

    def start(self):
        for s in self.symbols:
            sock = BinancePriceSocket(s)
            sock.start()
            self.sockets.append(sock)

    def stop(self):
        for s in self.sockets:
            if hasattr(s, "stop"):
                try:
                    s.stop()
                except Exception:
                    pass
        self.sockets = []
