import os
import unittest
from unittest.mock import patch

from src.providers.asin_dev import AsinDevAdapter


class AsinDevAdapterTests(unittest.TestCase):
    def test_normalizes_tracked_product(self):
        adapter = AsinDevAdapter(api_key="test")
        adapter._watchlist = lambda: [{
            "asin": "B09DFCB66S",
            "marketplace": "com",
            "product_id": "product-1",
        }]
        adapter._request = lambda method, path, **kwargs: {
            "asin": "B09DFCB66S",
            "marketplace": "com",
            "product_id": "product-1",
            "title": "Test headphones",
            "url": "https://www.amazon.com/dp/B09DFCB66S",
            "price": 79.99,
            "currency": "USD",
        }
        products = adapter.fetch([{"asin": "B09DFCB66S", "marketplace": "com"}])
        self.assertEqual(products[0]["price"], 79.99)
        self.assertEqual(products[0]["currency"], "USD")
        self.assertEqual(products[0]["store"], "amazon.com")

    def test_rejects_invalid_asin(self):
        adapter = AsinDevAdapter(api_key="test")
        adapter._watchlist = lambda: []
        with self.assertRaises(ValueError):
            adapter.fetch([{"asin": "BAD", "marketplace": "de"}])

    def test_turkey_marketplace_is_rejected_explicitly(self):
        adapter = AsinDevAdapter(api_key="test")
        adapter._watchlist = lambda: []
        with self.assertRaisesRegex(ValueError, "Amazon Turkey"):
            adapter.fetch([{"asin": "B09DFCB66S", "marketplace": "tr"}])

    def test_missing_api_key_is_clear_error(self):
        with patch.dict(os.environ, {"ASIN_API_KEY": ""}):
            with self.assertRaisesRegex(ValueError, "ASIN_API_KEY"):
                AsinDevAdapter(api_key="")


if __name__ == "__main__":
    unittest.main()
