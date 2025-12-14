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

        # settings
        self.root_dir = Path(__file__).resolve().parent
        self.settings_store = SettingsStore(self.root_dir)
        self.app_config = self.settings_store.load()  # <-- ใช้ชื่อนี้แทน config()

        # graceful shutdown
        self._closing = False
        self._poll_price_id = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.container = tk.Frame(self, bg="#0d0f1a")
        self.container.pack(fill="both", expand=True)

        self.pages = {}
        for Page in (WelcomePage, MainPage, GraphPage):
            page = Page(self.container, self)
            self.pages[Page.__name__] = page
            page.place(relwidth=1, relheight=1)

        self.show_page("WelcomePage")

        watchlist = self.app_config.get(
            "watchlist",
            ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"],
        )
        symbols_lower = [s.lower() for s in watchlist]

        self.price_service = PriceService(symbols_lower)
        self.price_service.start()

        self._poll_price_id = self.after(100, self._poll_price_queue)

    def show_page(self, name):
        self.pages[name].tkraise()

    def _poll_price_queue(self):
        if self._closing or not self.winfo_exists():
            return

        main_page = self.pages.get("MainPage")
        graph_page = self.pages.get("GraphPage")

        try:
            while True:
                sym, price = price_queue.get_nowait()
                sym = sym.upper()

                if main_page and hasattr(main_page, "update_price"):
                    main_page.update_price(sym, price)

                # อัปเดตราคาที่ header ใน GraphPage (ถ้าอยู่หน้า Graph)
                if graph_page and hasattr(graph_page, "on_price"):
                    graph_page.on_price(sym, price)

        except queue.Empty:
            pass

        self._poll_price_id = self.after(100, self._poll_price_queue)

    def on_close(self):
        self._closing = True

        if self._poll_price_id:
            try:
                self.after_cancel(self._poll_price_id)
            except Exception:
                pass
            self._poll_price_id = None

        # stop sockets/services
        if getattr(self, "price_service", None) and hasattr(self.price_service, "stop"):
            try:
                self.price_service.stop()
            except Exception:
                pass

        # allow pages to cleanup
        for p in self.pages.values():
            if hasattr(p, "on_close"):
                try:
                    p.on_close()
                except Exception:
                    pass

        # save settings
        try:
            self.settings_store.data = self.app_config
            self.settings_store.save()
        except Exception:
            pass

        try:
            self.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    App().mainloop()
