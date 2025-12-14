import tkinter as tk
import queue

from pages.welcome_page import WelcomePage
from pages.main_page import MainPage
from pages.graph_page import GraphPage

from data.price_service import PriceService
from queues.price_queue import price_queue

from queues.orderbook_queue import orderbook_queue
from data.orderbook_service import OrderBookService
from data.data_store import market_data

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Crypto Board")
        self.geometry("1200x700")
        self.configure(bg="#0d0f1a")

        self.container = tk.Frame(self, bg="#0d0f1a")
        self.container.pack(fill="both", expand=True)

        self.pages = {}
        for Page in (WelcomePage, MainPage, GraphPage):
            page = Page(self.container, self)
            self.pages[Page.__name__] = page
            page.place(relwidth=1, relheight=1)

        self.show_page("WelcomePage")

        self.price_service = PriceService(["btcusdt", "ethusdt", "bnbusdt"])
        self.price_service.start()
        self.after(100, self._poll_price_queue)



    def show_page(self, name):
        self.pages[name].tkraise()

    def _poll_price_queue(self):
        main_page = self.pages.get("MainPage")

        try:
            while True:
                sym, price = price_queue.get_nowait()
                if main_page and hasattr(main_page, "update_price"):
                    main_page.update_price(sym, price)
        except queue.Empty:
            pass

        self.after(100, self._poll_price_queue)





if __name__ == "__main__":
    app = App()
    app.mainloop()

