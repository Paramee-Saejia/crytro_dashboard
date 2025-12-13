import tkinter as tk
from tkinter import ttk
import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(1)


class GraphPage(tk.Frame):
    def __init__(self, parent, controller, symbol="DASH"):
        super().__init__(parent, bg="#0f111a")
        self.controller = controller
        self.symbol = symbol

        self._build_header()
        self._build_body()

    # ================= HEADER =================

    def _build_header(self):
        header = tk.Frame(self, bg="#0f111a", height=60)
        header.pack(fill="x", padx=24, pady=(16, 8))

        back_btn = tk.Button(
            header,
            text="←",
            font=("Segoe UI", 14),
            fg="white",
            bg="#0f111a",
            bd=0,
            activebackground="#0f111a",
            command=lambda: self.controller.show_page("MainPage")
        )
        back_btn.pack(side="left")

        title = tk.Label(
            header,
            text=f"{self.symbol} / THB",
            fg="white",
            bg="#0f111a",
            font=("Segoe UI", 18, "bold")
        )
        title.pack(side="left", padx=12)

        price = tk.Label(
            header,
            text="THB 1,447.75",
            fg="#ff5c5c",
            bg="#0f111a",
            font=("Segoe UI", 16, "bold")
        )
        price.pack(side="right")

    # ================= BODY =================

    def _build_body(self):
        body = tk.Frame(self, bg="#0f111a")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=3)
        body.rowconfigure(1, weight=2)

        self._chart_panel(body)
        self._stats_panel(body)
        self._orderbook_panel(body)
        self._volume_panel(body)

    # ================= PANELS =================

    def _panel(self, parent):
        return tk.Frame(parent, bg="#151823", padx=16, pady=16)

    def _chart_panel(self, parent):
        panel = self._panel(parent)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12))

        tk.Label(
            panel,
            text="Price Chart (1D)",
            fg="white",
            bg="#151823",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        canvas = tk.Canvas(
            panel,
            bg="#1b1f2e",
            highlightthickness=0
        )
        canvas.pack(fill="both", expand=True, pady=12)

        canvas.create_line(
            20, 120, 80, 90, 140, 130, 200, 80,
            260, 100, 320, 70, 380, 110,
            smooth=True,
            fill="#4da3ff",
            width=2
        )

    def _stats_panel(self, parent):
        panel = self._panel(parent)
        panel.grid(row=0, column=1, sticky="nsew", pady=(0, 12))

        self._stat(panel, "Market Cap", "THB 18.18B")
        self._stat(panel, "24h Volume", "THB 3.08B")
        self._stat(panel, "Circulating Supply", "13M DASH")

    def _orderbook_panel(self, parent):
        panel = self._panel(parent)
        panel.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(
            panel,
            text="Order Book",
            fg="white",
            bg="#151823",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))

        table = tk.Frame(panel, bg="#151823")
        table.pack(fill="both", expand=True)

        self._order_column(table, "ASK", "#ff5c5c")
        self._order_column(table, "BID", "#3ddc97")

    def _volume_panel(self, parent):
        panel = self._panel(parent)
        panel.grid(row=1, column=1, sticky="nsew")

        self._stat(panel, "Buy Volume (1H)", "10.90")
        self._stat(panel, "Sell Volume (1H)", "8.97")
        self._stat(panel, "Buy / Sell Ratio", "0.95")

    # ================= COMPONENTS =================

    def _stat(self, parent, title, value):
        box = tk.Frame(parent, bg="#1b1f2e", pady=8)
        box.pack(fill="x", pady=6)

        tk.Label(
            box,
            text=title,
            fg="#9aa4c7",
            bg="#1b1f2e",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        tk.Label(
            box,
            text=value,
            fg="white",
            bg="#1b1f2e",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

    def _order_column(self, parent, title, color):
        col = tk.Frame(parent, bg="#151823")
        col.pack(side="left", expand=True, fill="both", padx=8)

        tk.Label(
            col,
            text=title,
            fg=color,
            bg="#151823",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 6))

        for _ in range(5):
            tk.Label(
                col,
                text="700.09   |   50.00",
                fg="white",
                bg="#151823",
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=2)


if __name__ == "__main__":
    import tkinter as tk

    class _MockController:
        def show_page(self, name):
            print("Navigate to:", name)

    root = tk.Tk()
    root.title("GraphPage Test")
    root.geometry("1200x700")
    root.configure(bg="#0f111a")

    page = GraphPage(root, _MockController(), symbol="DASH")
    page.pack(fill="both", expand=True)

    root.mainloop()
