import tkinter as tk
import queue
from pathlib import Path

from pages.welcome_page import WelcomePage
from pages.main_page import MainPage
from pages.graph_page import GraphPage

from data.price_service import PriceService
from queues.price_queue import price_queue

from data.settings_store import SettingsStore


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Crypto Board")
        self.geometry("1200x700")
        self.configure(bg="#0d0f1a")

        self.root_dir = Path(__file__).resolve().parent
        self.settings = SettingsStore(self.root_dir)
        self.config = self.settings.load()

        self.container = tk.Frame(self, bg="#0d0f1a")
        self.container.pack(fill="both", expand=True)

        self.pages = {}
        for Page in (WelcomePage, MainPage, GraphPage):
            page = Page(self.container, self)
            self.pages[Page.__name__] = page
            page.place(relwidth=1, relheight=1)

        self.show_page("WelcomePage")

        watchlist = self.config.get(
            "watchlist",
            ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"],
        )
        symbols_lower = [s.lower() for s in watchlist]

        self.price_service = PriceService(symbols_lower)
        self.price_service.start()

        self.after(100, self._poll_price_queue)

    def show_page(self, name):
        self.pages[name].tkraise()

    def _poll_price_queue(self):
        main_page = self.pages.get("MainPage")

        try:
            while True:
                sym, price = price_queue.get_nowait()
                sym = sym.upper()

                if main_page and hasattr(main_page, "update_price"):
                    main_page.update_price(sym, price)
        except queue.Empty:
            pass

        self.after(100, self._poll_price_queue)


if __name__ == "__main__":
    app = App()
    app.mainloop()
