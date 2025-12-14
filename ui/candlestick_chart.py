import tkinter as tk
import mplfinance as mpf
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from bisect import bisect_left

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from data.kline_client import fetch_klines


class CandlestickChart(tk.Frame):
    def __init__(self, parent, on_hover=None):
        super().__init__(parent, bg="#151823", padx=16, pady=16)

        tk.Label(
            self,
            text="Price Chart",
            fg="white",
            bg="#151823",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")

        self._symbol = "BTCUSDT"
        self._interval = "1m"
        self._df = None

        self._on_hover = on_hover
        self._x_vals = []
        self._x_mode = "date"   # "date" or "index"
        self._last_i = None

        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor("#151823")
        self.ax.set_facecolor("#1b1f2e")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=12)

        self._vline = self.ax.axvline(0, color="#6b7280", linewidth=1, linestyle="--", alpha=0.5)
        self._vline.set_visible(False)

        self.canvas.mpl_connect("motion_notify_event", self._on_move)
        self.canvas.mpl_connect("figure_leave_event", self._on_leave)

    def set_symbol(self, symbol: str, interval: str = "1m"):
        self._symbol = symbol.upper()
        self._interval = interval
        self.refresh()

    def refresh(self):
        self._df = fetch_klines(self._symbol, interval=self._interval, limit=120)
        self._draw()

    def _draw(self):
        if self._df is None or self._df.empty:
            return

        self._last_i = None

        self.ax.clear()
        self.ax.set_facecolor("#1b1f2e")

        mc = mpf.make_marketcolors(
            up="#3ddc97",
            down="#ff5c5c",
            edge="inherit",
            wick="inherit",
        )
        style = mpf.make_mpf_style(
            base_mpf_style="nightclouds",
            marketcolors=mc,
            facecolor="#1b1f2e",
            figcolor="#151823",
            gridcolor="#2a2f45",
            rc={
                "axes.labelcolor": "white",
                "xtick.color": "white",
                "ytick.color": "white",
                "axes.edgecolor": "white",
            },
        )

        mpf.plot(
            self._df,
            type="candle",
            ax=self.ax,
            style=style,
            show_nontrading=False,
            datetime_format="%H:%M",
            xrotation=0,
            update_width_config={
                "candle_width": 0.7,
                "candle_linewidth": 1.0,
            },
        )

        # format axes
        self.ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.2f}"))
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=9))
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        for spine in self.ax.spines.values():
            spine.set_color("white")
        self.ax.tick_params(axis="x", colors="white", labelsize=9)
        self.ax.tick_params(axis="y", colors="white", labelsize=9)

        self.fig.subplots_adjust(left=0.06, right=0.985, top=0.96, bottom=0.20)

        # detect x-axis mode used by mplfinance (some versions use index scale)
        x0, x1 = self.ax.get_xlim()
        if x1 < (len(self._df) * 5):
            self._x_mode = "index"
            self._x_vals = list(range(len(self._df)))
        else:
            self._x_mode = "date"
            self._x_vals = list(mdates.date2num(self._df.index.to_pydatetime()))

        self._vline = self.ax.axvline(0, color="#6b7280", linewidth=1, linestyle="--", alpha=0.5)
        self._vline.set_visible(False)

        self.canvas.draw_idle()

    def _nearest_index(self, xdata: float):
        if self._df is None:
            return None
        n = len(self._df)
        if n == 0:
            return None

        if self._x_mode == "index":
            i = int(round(xdata))
            if i < 0:
                i = 0
            if i >= n:
                i = n - 1
            return i

        xs = self._x_vals
        if not xs:
            return None
        j = bisect_left(xs, xdata)
        if j <= 0:
            return 0
        if j >= n:
            return n - 1
        left = xs[j - 1]
        right = xs[j]
        return j - 1 if abs(xdata - left) <= abs(xdata - right) else j

    def _on_move(self, event):
        if self._df is None or event.inaxes != self.ax or event.xdata is None:
            return

        i = self._nearest_index(event.xdata)
        if i is None or i == self._last_i:
            return

        self._last_i = i
        row = self._df.iloc[i]
        close = float(row["close"])

        if i > 0:
            prev_close = float(self._df.iloc[i - 1]["close"])
            pct = ((close - prev_close) / prev_close) * 100.0 if prev_close != 0 else 0.0
        else:
            pct = 0.0

        # show crosshair without redrawing whole chart
        xpos = self._x_vals[i] if self._x_vals else event.xdata
        self._vline.set_xdata([xpos, xpos])
        self._vline.set_visible(True)
        self.canvas.draw_idle()

        # send to parent (GraphPage/Header)
        if callable(self._on_hover):
            self._on_hover(close, pct)

    def _on_leave(self, event):
        if self._vline is not None:
            self._vline.set_visible(False)
        self._last_i = None
        self.canvas.draw_idle()
