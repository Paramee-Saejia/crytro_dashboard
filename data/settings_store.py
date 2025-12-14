import json
from pathlib import Path

DEFAULTS = {
    "watchlist": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"],
    "panels": {"stats": True, "orderbook": True, "volume": True},
}

class SettingsStore:
    def __init__(self, root_dir: Path):
        self.path = root_dir / "settings.json"
        self.data = {}

    def load(self):
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self.data = dict(DEFAULTS)
        else:
            self.data = dict(DEFAULTS)
            self.save()

        # normalize
        self.data.setdefault("watchlist", DEFAULTS["watchlist"][:])
        self.data.setdefault("panels", dict(DEFAULTS["panels"]))
        return self.data

    def save(self):
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
