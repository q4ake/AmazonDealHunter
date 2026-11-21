"""Scavio adapter for Amazon marketplaces, including Amazon Turkey."""
import os
import re

import requests


BASE_URL = "https://api.scavio.dev/api/v1"


class ScavioAdapter:
    """Fetch current Amazon product prices by ASIN through Scavio."""

    def __init__(self, api_key=None, timeout=30):
        self.api_key = api_key or os.getenv("SCAVIO_API_KEY")
        if not self.api_key:
            raise ValueError(
                "SCAVIO_API_KEY is missing. Add your Scavio API key to the .env file."
            )
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def _request_product(self, asin, country="tr", language="TR"):
        response = self.session.post(
            f"{BASE_URL}/amazon/product",
            json={"query": asin, "country": country, "language": language},
            timeout=self.timeout,
        )
        try:
            payload = response.json()
        except ValueError:
            response.raise_for_status()
            raise RuntimeError("Scavio API returned a non-JSON response.")

        if not response.ok:
            error = payload.get("error", {})
            message = error.get("message") or payload.get("message") or response.text
            code = error.get("code")
            suffix = f" ({code})" if code else ""
            raise RuntimeError(f"Scavio API {response.status_code}{suffix}: {message}")

        data = payload.get("data")
        if not isinstance(data, dict):
            raise RuntimeError("Scavio API response is missing the 'data' object.")
        return data

    def fetch(self, items):
        """Return normalized products for [{asin, country?, language?}, ...]."""
        results = []
        for item in items:
            asin = str(item.get("asin", "")).strip().upper()
            if not re.fullmatch(r"[A-Z0-9]{10}", asin):
                raise ValueError(f"Invalid ASIN: {asin!r}")

            country = str(item.get("country", "tr")).strip().lower()
            language = str(item.get("language", "TR")).strip().upper()
            if country != "tr":
                raise ValueError(
                    f"This product list is configured for Amazon Turkey; "
                    f"got country={country!r}. Use country='tr'."
                )

            product = self._request_product(asin, country=country, language=language)
            price = product.get("price")
            if price is None or float(price) <= 0:
                print(f"No current price available for {asin}; skipped")
                continue

            results.append({
                "asin": asin,
                "title": product.get("title") or asin,
                "url": product.get("url") or f"https://www.amazon.com.tr/dp/{asin}",
                "price": float(price),
                "currency": product.get("currency") or "TRY",
                "store": "amazon.com.tr",
            })

        return results
