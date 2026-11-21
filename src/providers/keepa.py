"""Keepa API adapter for marketplaces supported by Keepa."""

import os
import re
import requests


MARKETPLACES = {
    "us": {"domain": 1, "host": "www.amazon.com", "currency": "USD", "scale": 100},
    "uk": {"domain": 2, "host": "www.amazon.co.uk", "currency": "GBP", "scale": 100},
    "de": {"domain": 3, "host": "www.amazon.de", "currency": "EUR", "scale": 100},
    "fr": {"domain": 4, "host": "www.amazon.fr", "currency": "EUR", "scale": 100},
    "jp": {"domain": 5, "host": "www.amazon.co.jp", "currency": "JPY", "scale": 1},
    "ca": {"domain": 6, "host": "www.amazon.ca", "currency": "CAD", "scale": 100},
    "it": {"domain": 8, "host": "www.amazon.it", "currency": "EUR", "scale": 100},
    "es": {"domain": 9, "host": "www.amazon.es", "currency": "EUR", "scale": 100},
    "in": {"domain": 10, "host": "www.amazon.in", "currency": "INR", "scale": 100},
    "mx": {"domain": 11, "host": "www.amazon.com.mx", "currency": "MXN", "scale": 100},
    "br": {"domain": 12, "host": "www.amazon.com.br", "currency": "BRL", "scale": 100},
}


class KeepaAdapter:
    """Fetch current Amazon prices by ASIN through the paid Keepa API."""

    def __init__(self, api_key=None, timeout=20):
        self.api_key = api_key or os.getenv("KEEPA_API_KEY")
        if not self.api_key:
            raise ValueError("KEEPA_API_KEY is missing. Add your Keepa API key to .env.")
        self.timeout = timeout
        self.session = requests.Session()

    @staticmethod
    def _price(product, scale):
        stats = product.get("stats") or {}
        current = stats.get("current") or []
        # Keepa CSV price type 0 = Amazon; 1 = marketplace new.
        for index in (0, 1):
            if len(current) > index and isinstance(current[index], (int, float)) and current[index] > 0:
                return current[index] / scale
        return None

    def fetch(self, items):
        """Return normalized products for [{asin, marketplace}, ...]."""
        grouped = {}
        for item in items:
            asin = str(item.get("asin", "")).strip().upper()
            marketplace = str(item.get("marketplace", "de")).strip().lower()
            if not re.fullmatch(r"[A-Z0-9]{10}", asin):
                raise ValueError(f"Invalid ASIN: {asin!r}")
            if marketplace not in MARKETPLACES:
                supported = ", ".join(sorted(MARKETPLACES))
                raise ValueError(
                    f"Keepa does not support marketplace '{marketplace}'. Supported: {supported}. "
                    "Amazon Turkey (tr) is not currently available through Keepa."
                )
            grouped.setdefault(marketplace, []).append(asin)

        results = []
        for marketplace, asins in grouped.items():
            config = MARKETPLACES[marketplace]
            # Keepa accepts up to 100 ASINs per product request.
            for offset in range(0, len(asins), 100):
                batch = asins[offset:offset + 100]
                response = self.session.get(
                    "https://api.keepa.com/product",
                    params={
                        "key": self.api_key,
                        "domain": config["domain"],
                        "asin": ",".join(batch),
                        "stats": 30,
                        "history": 0,
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()
                payload = response.json()
                if payload.get("error"):
                    error = payload["error"]
                    raise RuntimeError(f"Keepa API error: {error.get('message', error)}")

                by_asin = {p.get("asin", "").upper(): p for p in payload.get("products", [])}
                for asin in batch:
                    product = by_asin.get(asin)
                    if not product:
                        print(f"Keepa returned no product for ASIN {asin}")
                        continue
                    price = self._price(product, config["scale"])
                    if price is None:
                        print(f"No current Amazon/new price available for {asin}; skipped")
                        continue
                    results.append({
                        "asin": asin,
                        "title": product.get("title") or asin,
                        "url": f"https://{config['host']}/dp/{asin}",
                        "price": round(price, 2),
                        "currency": config["currency"],
                        "store": f"amazon.{marketplace}",
                    })
        return results
