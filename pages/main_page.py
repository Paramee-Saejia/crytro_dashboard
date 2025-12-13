import tkinter as tk
from PIL import Image, ImageTk

CRYPTO_ICON_PATHS = {
    "BTC": r"images\icon_Cryptro\bitcoin.png",
    "ETH": r"images\icon_Cryptro\eth.png",
    "USTD": r"images\icon_Cryptro\USTD.png"
}


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1b1b2f")
        self.controller = controller

        self.icon_images = {}
        self.load_icons()

        tk.Label(
            self,
            text="Main Page",
            bg="#1b1b2f",
            fg="white",
            font=("Arial", 16)
        ).pack(pady=20)

        tk.Button(
            self,
            text="Go to Graph",
            command=lambda: self.controller.show_page("GraphPage")
        ).pack(pady=10)

        self.create_crypto_card("BTC", "5 seconds ago", "↓2.64%", "$12,729", "$500B", "$30B")
        self.create_crypto_card("ETH", "5 seconds ago", "↓1.23%", "$1,234", "$200B", "$10B")
        self.create_crypto_card("USTD", "↑0.56%", "$300", "$50B", "$2B", "$2B")

    def load_icons(self):
        for symbol, path in CRYPTO_ICON_PATHS.items():
            img = Image.open(path).resize((30, 30), Image.LANCZOS)
            self.icon_images[symbol] = img

    def create_crypto_card(self, crypto, updated, change, price, market_cap, volume):
        card = tk.Frame(self, bg="#2a2a40", padx=10, pady=10)
        card.pack(pady=10, fill="x", padx=20)

        pil_img = self.icon_images.get(crypto)
        if pil_img:
            photo = ImageTk.PhotoImage(pil_img, master=self)
            lbl = tk.Label(card, image=photo, bg="#2a2a40")
            lbl.image = photo
            lbl.grid(row=1, column=0, padx=5)

        headers = ["Crypto", "Updated", "Change", "Price", "Market Cap", "Volume"]
        for i, h in enumerate(headers):
            tk.Label(card, text=h, bg="#2a2a40", fg="white").grid(row=0, column=i+1)

        values = [crypto, updated, change, price, market_cap, volume]
        for i, v in enumerate(values):
            tk.Label(card, text=v, bg="#2a2a40", fg="white").grid(row=1, column=i+1)
