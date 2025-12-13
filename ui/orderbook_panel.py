import tkinter as tk


class OrderBookPanel(tk.Frame):
    def __init__(self, parent, rows=10):
        super().__init__(parent, bg="#151823", padx=16, pady=16)
        self.rows = rows

        tk.Label(
            self,
            text="Order Book",
            fg="white",
            bg="#151823",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        table = tk.Frame(self, bg="#151823")
        table.pack(fill="both", expand=True)

        tk.Label(
            table, text="ASK", fg="#ff5c5c", bg="#151823",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=8, pady=(0, 6))

        tk.Label(
            table, text="BID", fg="#3ddc97", bg="#151823",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=1, sticky="w", padx=8, pady=(0, 6))

        self.ask_labels = []
        self.bid_labels = []

        for i in range(self.rows):
            a = tk.Label(table, text="", fg="#ff5c5c", bg="#151823", font=("Segoe UI", 10))
            b = tk.Label(table, text="", fg="#3ddc97", bg="#151823", font=("Segoe UI", 10))
            a.grid(row=i + 1, column=0, sticky="w", padx=8, pady=2)
            b.grid(row=i + 1, column=1, sticky="w", padx=8, pady=2)
            self.ask_labels.append(a)
            self.bid_labels.append(b)

    def render(self, bids, asks):
        asks_view = asks[: self.rows]
        bids_view = bids[: self.rows]

        for i in range(self.rows):
            if i < len(asks_view):
                p, q = asks_view[i]
                self.ask_labels[i].config(text=f"{p} | {q}")
            else:
                self.ask_labels[i].config(text="")

            if i < len(bids_view):
                p, q = bids_view[i]
                self.bid_labels[i].config(text=f"{p} | {q}")
            else:
                self.bid_labels[i].config(text="")
