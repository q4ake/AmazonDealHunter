import unittest

from src.providers.keepa import KeepaAdapter, MARKETPLACES


class KeepaAdapterTests(unittest.TestCase):
    def test_amazon_price_is_preferred(self):
        product = {"stats": {"current": [12999, 13999]}}
        self.assertEqual(KeepaAdapter._price(product, 100), 129.99)

    def test_new_price_is_fallback(self):
        product = {"stats": {"current": [-1, 4599]}}
        self.assertEqual(KeepaAdapter._price(product, 100), 45.99)

    def test_unavailable_price_returns_none(self):
        product = {"stats": {"current": [-1, -1]}}
        self.assertIsNone(KeepaAdapter._price(product, 100))

    def test_japanese_yen_has_no_decimal_scaling(self):
        self.assertEqual(KeepaAdapter._price({"stats": {"current": [1500]}}, 1), 1500)

    def test_turkey_is_not_claimed_as_keepa_marketplace(self):
        self.assertNotIn("tr", MARKETPLACES)


if __name__ == "__main__":
    unittest.main()
