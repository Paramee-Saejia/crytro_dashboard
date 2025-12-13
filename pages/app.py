import tkinter as tk
from welcome_page import WelcomePage
from graph_page import GraphPage
from main_page import MainPage


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

    def show_page(self, name):
        self.pages[name].tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()
