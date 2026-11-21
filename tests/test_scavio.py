import os
import unittest
from unittest.mock import Mock, patch

from src.providers.scavio import ScavioAdapter


class ScavioAdapterTests(unittest.TestCase):
    def test_normalizes_turkish_product(self):
        adapter = ScavioAdapter(api_key="test")
        adapter._request_product = lambda asin, country, language: {
            "asin": asin,
            "title": "Hot Wheels test car",
            "url": "https://www.amazon.com.tr/dp/B0ABC12345",
            "price": 249.90,
            "currency": "TRY",
        }
        products = adapter.fetch([{"asin": "B0ABC12345"}])
        self.assertEqual(products[0]["price"], 249.90)
        self.assertEqual(products[0]["currency"], "TRY")
        self.assertEqual(products[0]["store"], "amazon.com.tr")

    def test_sends_turkey_and_turkish_language(self):
        adapter = ScavioAdapter(api_key="test")
        adapter._request_product = Mock(return_value={
            "price": 100, "currency": "TRY"
        })
        adapter.fetch([{"asin": "B0ABC12345"}])
        adapter._request_product.assert_called_once_with(
            "B0ABC12345", country="tr", language="TR"
        )

    def test_rejects_invalid_asin(self):
        adapter = ScavioAdapter(api_key="test")
        with self.assertRaises(ValueError):
            adapter.fetch([{"asin": "BAD"}])

    def test_rejects_non_turkey_country_for_this_list(self):
        adapter = ScavioAdapter(api_key="test")
        with self.assertRaisesRegex(ValueError, "Amazon Turkey"):
            adapter.fetch([{"asin": "B0ABC12345", "country": "de"}])

    def test_missing_api_key_is_clear_error(self):
        with patch.dict(os.environ, {"SCAVIO_API_KEY": ""}):
            with self.assertRaisesRegex(ValueError, "SCAVIO_API_KEY"):
                ScavioAdapter(api_key="")


if __name__ == "__main__":
    unittest.main()
