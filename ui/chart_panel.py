import tkinter as tk


class ChartPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#151823", padx=16, pady=16)

        tk.Label(
            self,
            text="Price Chart (1D)",
            fg="white",
            bg="#151823",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")

        canvas = tk.Canvas(self, bg="#1b1f2e", highlightthickness=0)
        canvas.pack(fill="both", expand=True, pady=12)

        canvas.create_line(
            20, 120, 80, 90, 140, 130, 200, 80,
            260, 100, 320, 70, 380, 110,
            smooth=True,
            fill="#4da3ff",
            width=2,
        )
