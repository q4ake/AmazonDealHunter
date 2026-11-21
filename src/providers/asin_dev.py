"""Asin.dev adapter for free daily Amazon product tracking.

The provider performs the scheduled Amazon checks on its side. This adapter
reads the latest tracked-product values and registers a product once when it
is not already in the account watchlist.
"""
import os
import requests


BASE_URL = "https://www.asin.dev/api/v1"


class AsinDevAdapter:
    def __init__(self, api_key=None, timeout=30):
        self.api_key = api_key or os.getenv("ASIN_API_KEY")
        if not self.api_key:
            raise ValueError("ASIN_API_KEY is missing. Add it to your .env or GitHub Actions secrets.")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _request(self, method, path, **kwargs):
        response = self.session.request(
            method, f"{BASE_URL}{path}", timeout=self.timeout, **kwargs
        )
        try:
            payload = response.json()
        except ValueError:
            response.raise_for_status()
            raise RuntimeError("Asin API returned a non-JSON response.")
        if not response.ok:
            error = payload.get("error", {})
            code = error.get("code", "api_error")
            message = error.get("message", response.text)
            raise RuntimeError(f"Asin API {response.status_code} ({code}): {message}")
        return payload

    def _watchlist(self):
        payload = self._request("GET", "/products?filter=all&limit=100")
        return payload.get("products", [])

    def fetch(self, items):
        """Return normalized products for [{asin, marketplace, target_price?}]."""
        tracked = self._watchlist()
        by_key = {
            (str(p.get("asin", "")).upper(), str(p.get("marketplace", "")).lower()): p
            for p in tracked
        }
        results = []

        for item in items:
            asin = str(item.get("asin", "")).strip().upper()
            marketplace = str(item.get("marketplace", "de")).strip().lower()
            if len(asin) != 10 or not asin.isalnum():
                raise ValueError(f"Invalid ASIN: {asin!r}")

            key = (asin, marketplace)
            product = by_key.get(key)
            if product is None:
                body = {
                    "product": asin,
                    "marketplace": marketplace,
                    "interval_minutes": 1440,
                    "wait": True,
                }
                if item.get("target_price") is not None:
                    body["target_price"] = float(item["target_price"])
                product = self._request("POST", "/products", json=body)
                by_key[key] = product

            product_id = product.get("product_id")
            if product_id:
                # Refresh status/current price; this read does not initiate a new Amazon check.
                product = self._request("GET", f"/products/{product_id}")

            if product.get("last_error"):
                print(
                    f"Asin provider status for {asin}: "
                    f"{product['last_error']} (status={product.get('status', 'unknown')})"
                )
            price = product.get("price")
            if price is None:
                print(f"No current price available for {asin}; status={product.get('status')}")
                continue

            results.append({
                "asin": asin,
                "title": product.get("title") or asin,
                "url": product.get("url") or f"https://www.amazon.{marketplace}/dp/{asin}",
                "price": float(price),
                "currency": product.get("currency") or "EUR",
                "store": f"amazon.{marketplace}",
            })

        return results
