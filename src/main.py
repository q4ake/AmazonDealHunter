import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from src.notifier import TelegramNotifier
from src.storage import PriceStorage


def load_products(path: str):
    with open(path, "r", encoding="utf-8") as file:
        products = json.load(file)
    if not isinstance(products, list):
        raise ValueError("Ürün dosyası bir JSON listesi olmalıdır.")
    required = {"asin", "title", "url", "price", "currency", "store"}
    for index, product in enumerate(products):
        missing = required - product.keys()
        if missing:
            raise ValueError(f"{index}. üründe eksik alanlar: {', '.join(sorted(missing))}")
        if float(product["price"]) <= 0:
            raise ValueError(f"{index}. ürünün fiyatı sıfırdan büyük olmalıdır.")
    return products


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="AmazonDealHunter demo price tracker")
    parser.add_argument("--input", default="data/products.example.json")
    args = parser.parse_args()

    database_path = os.getenv("DATABASE_PATH", "data/prices.db")
    min_discount = float(os.getenv("MIN_DISCOUNT_PERCENT", "5"))
    storage = PriceStorage(database_path)
    notifier = TelegramNotifier(
        os.getenv("TELEGRAM_BOT_TOKEN", ""),
        os.getenv("TELEGRAM_CHAT_ID", ""),
    )

    products = load_products(args.input)
    for product in products:
        previous = storage.add_price(product)
        if previous is None:
            print(f"İlk kayıt: {product['title']} — {product['price']} {product['currency']}")
            continue

        if previous > 0 and float(product["price"]) < previous:
            discount = (previous - float(product["price"])) / previous * 100
            message = (
                f"Fiyat düştü!\n{product['title']}\n"
                f"Eski fiyat: {previous:.2f} {product['currency']}\n"
                f"Yeni fiyat: {float(product['price']):.2f} {product['currency']}\n"
                f"İndirim: %{discount:.1f}\n{product['url']}"
            )
            if discount >= min_discount:
                notifier.send(message)
            else:
                print(message)
        else:
            print(f"Fiyat kaydedildi: {product['title']} — {product['price']} {product['currency']}")


if __name__ == "__main__":
    main()
