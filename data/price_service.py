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
