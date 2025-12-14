# Crypto Board (Tkinter Real-Time Dashboard)

A real-time cryptocurrency dashboard built with **Python + Tkinter**.  
The app streams **live prices** and **order book updates** from **Binance WebSocket**, and provides a **candlestick chart** and **24h market stats** for selected assets.

---

## Project Overview

This is a desktop crypto dashboard featuring:
- **Multi-page UI** (Welcome → Assets list → Detailed asset page)
- **Real-time price streaming** via Binance WebSocket (`@trade`)
- **Order book** (top 10 bids/asks) via Binance WebSocket (`@depth10@100ms`)
- **Candlestick chart** using Matplotlib / mplfinance (Binance REST klines)
- **24h market stats** using Binance REST API (`/api/v3/ticker/24hr`)
- **Panel toggles** to show/hide **Stats / Order Book / Volume** panels
- **Saved preferences** (watchlist + panel visibility) stored in JSON (`settings.json`)

---

## Features Checklist (Requirements)

### 1) Basic Functionality
- [x] Application launches without errors
- [x] Clean OOP design with classes (App, Pages, UI Panels, Services)
- [x] Proper event handling (Tkinter callbacks + scheduled `after()` updates)
- [x] Graceful shutdown (stops WebSocket threads/services; saves settings)

### 2) Price Tickers
- [x] At least 3 cryptocurrency tickers (BTC, ETH, SOL)
- [x] Real-time price updates via WebSocket
- [x] Color-coded price changes (green/red) on the detail page header
- [x] Display 24h change and percentage (Stats panel via REST API)

### 3) User Interface
- [x] Professional, organized layout
- [x] Toggle buttons to show/hide panels (Stats / Order Book / Volume)
- [x] Responsive to window resizing (grid weights on Graph page)
- [x] Clear labeling and readability

### 4) Additional Data Streams (Advanced)
- [x] 24h Volume display (Quote Volume shown in Stats panel)
- [x] Order Book (top 10 bids/asks via depth stream)
- [ ] Recent Trades feed (not implemented)
- [x] Candlestick chart with matplotlib (mplfinance)

### 5) Multiple Assets & Toggles (Advanced)
- [x] Support for 5+ cryptocurrencies (default watchlist = 5)
- [ ] Individual toggle buttons for each asset (not implemented; assets selectable from MainPage list)
- [x] Saved preferences (remembers which panels are visible)

### 6) Information Density (Advanced)
- [x] Displays comprehensive market data (price, 24h stats, order book, chart)
- [x] Multiple panels with different information types
- [x] Efficient use of screen space (2-column layout on detail page)

---

## Tech Stack
- **Python 3.x**
- **Tkinter** (GUI)
- **websocket-client** (Binance WebSocket streams)
- **requests** (Binance REST API)
- **pandas** (kline data parsing)
- **matplotlib + mplfinance** (candlestick chart)
- **Pillow** (icons)

---

dash_board/
├─ app.py
├─ requirements.txt
├─ settings.json
├─ pages/
│  ├─ __init__.py
│  ├─ welcome_page.py
│  ├─ main_page.py
│  └─ graph_page.py
├─ data/
│  ├─ __init__.py
│  ├─ data_store.py
│  ├─ settings_store.py
│  ├─ socket_client.py
│  ├─ price_service.py
│  ├─ orderbook_service.py
│  └─ kline_client.py
├─ queues/
│  ├─ __init__.py
│  ├─ price_queue.py
│  └─ orderbook_queue.py
├─ ui/
│  ├─ __init__.py
│  ├─ header_panel.py
│  ├─ candlestick_chart.py
│  ├─ stats_panel.py
│  ├─ orderbook_panel.py
│  └─ volume_panel.py
└─ images/
   └─ icon_Cryptro/
      ├─ bitcoin.png
      ├─ eth.png
      ├─ sol.png
      ├─ bnb.png
      └─ xrp.png


## What Each File Does (Quick Guide)

### Entry Point
- **app.py**  
  Application entry point. Creates the main Tk window, loads `settings.json`, initializes pages, starts the WebSocket price service, and polls `price_queue` to update MainPage/GraphPage.

### Pages (UI Screens)
- **pages/welcome_page.py**  
  Welcome screen with a button to navigate to the main dashboard.
- **pages/main_page.py**  
  Asset list screen (watchlist). Shows live prices and a **View** button to open the detail page.
- **pages/graph_page.py**  
  Asset detail screen. Displays the header price, candlestick chart, 24h stats, order book, volume panel, and panel toggle buttons.

### Data Layer (Networking / Settings / Store)
- **data/data_store.py**  
  Shared in-memory state (e.g., `market_data.prices`) used across pages/services.
- **data/settings_store.py**  
  Loads/saves user preferences in `settings.json` (watchlist + panel visibility).
- **data/socket_client.py**  
  Binance WebSocket clients using `websocket-client`:
  - `BinancePriceSocket` (`{symbol}@trade`) → pushes `(symbol, price)` into `price_queue`
  - `BinanceOrderBookSocket` (`{symbol}@depth10@100ms`) → pushes `(symbol, bids, asks)` into `orderbook_queue`  
  Includes `start()` / `stop()` helpers for clean shutdown.
- **data/price_service.py**  
  Manager that starts price sockets for all symbols in the watchlist.
- **data/orderbook_service.py** *(optional)*  
  Manager for starting multiple order book sockets (some versions start order book streams directly from `GraphPage`).
- **data/kline_client.py**  
  Fetches candlestick (kline) data via Binance REST (`/api/v3/klines`) and converts it into a DataFrame for plotting.

### Queues (Thread-safe Messaging)
- **queues/price_queue.py**  
  Thread-safe queue for sending price updates from WebSocket threads → Tkinter main thread.
- **queues/orderbook_queue.py**  
  Thread-safe queue for sending order book updates from WebSocket threads → Tkinter main thread.

### UI Components (Reusable Panels)
- **ui/header_panel.py**  
  Top header for GraphPage (back button, trading pair, live price).
- **ui/candlestick_chart.py**  
  Candlestick chart (mplfinance/matplotlib). Sends hover data back to the page (used to update the header).
- **ui/stats_panel.py**  
  Displays 24h stats (change %, high, low, quote volume) refreshed via REST in `graph_page.py`.
- **ui/orderbook_panel.py**  
  Renders top bids/asks (order book).
- **ui/volume_panel.py**  
  Volume panel UI. (Data logic depends on the selected approach and may be limited in the current version.)

----------------------------------

## How to Run

> Notes about virtual environment (venv):
> - Creating a venv is **recommended** to avoid dependency conflicts.
> - It is **not strictly required**. If you install dependencies globally, you can still run the project.
> - The main entry file is **`app.py`**.

### Option A (Recommended): Use a virtual environment

**use cmd**
``` cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py



