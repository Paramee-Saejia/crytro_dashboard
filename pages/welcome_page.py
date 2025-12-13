import tkinter as tk


class WelcomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0d0f1a")
        self.controller = controller

        title_frame = tk.Frame(self, bg="#0d0f1a")
        title_frame.place(relx=0.5, rely=0.4, anchor="center")

        tk.Label(
            title_frame,
            text="CRYPTO",
            fg="#FFFFFF",
            bg="#0d0f1a",
            font=("Paytone One", 52, "bold")
        ).pack(side="left", padx=(0, 10))

        tk.Label(
            title_frame,
            text="BOARD",
            fg="#7D67FF",
            bg="#0d0f1a",
            font=("Paytone One", 52, "bold")
        ).pack(side="left")

        tk.Button(
            self,
            text="click",
            font=("Paytone One", 20, "bold"),
            command=lambda: self.controller.show_page("MainPage")
        ).place(relx=0.5, rely=0.6, anchor="center")

