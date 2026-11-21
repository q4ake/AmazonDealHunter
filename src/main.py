import argparse
import json
import os

from dotenv import load_dotenv

from src.notifier import TelegramNotifier
from src.providers.keepa import KeepaAdapter
from src.providers.asin_dev import AsinDevAdapter
from src.providers.scavio import ScavioAdapter
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


def load_keepa_items(path: str):
    with open(path, "r", encoding="utf-8") as file:
        items = json.load(file)
    if not isinstance(items, list) or not items:
        raise ValueError("Ürün dosyası boş olmayan bir JSON listesi olmalıdır.")
    return items


def process_products(products, storage, notifier, min_discount):
    if not products:
        print("İşlenecek fiyat verisi bulunamadı.")
        return

    for product in products:
        previous = storage.add_price(product)
        if previous is None:
            print(f"İlk kayıt: {product['title']} — {product['price']:.2f} {product['currency']}")
            continue

        current = float(product["price"])
        if previous > 0 and current < previous:
            discount = (previous - current) / previous * 100
            message = (
                f"Fiyat düştü!\\n{product['title']}\\n"
                f"Eski fiyat: {previous:.2f} {product['currency']}\\n"
                f"Yeni fiyat: {current:.2f} {product['currency']}\\n"
                f"İndirim: %{discount:.1f}\\n{product['url']}"
            )
            if discount >= min_discount:
                notifier.send(message)
            else:
                print(message)
        else:
            print(f"Fiyat kaydedildi: {product['title']} — {current:.2f} {product['currency']}")


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="AmazonDealHunter price tracker")
    parser.add_argument("--provider", choices=("demo", "keepa", "asin", "scavio"), default="demo")
    parser.add_argument("--input", default=None, help="JSON product/ASIN list")
    args = parser.parse_args()

    default_input = (
        "data/products.keepa.example.json"
        if args.provider == "keepa"
        else "data/products.asin.example.json" if args.provider == "asin"
        else "data/products.scavio.example.json" if args.provider == "scavio"
        else "data/products.example.json"
    )
    input_path = args.input or default_input

    storage = PriceStorage(os.getenv("DATABASE_PATH", "data/prices.db"))
    notifier = TelegramNotifier(
        os.getenv("TELEGRAM_BOT_TOKEN", ""),
        os.getenv("TELEGRAM_CHAT_ID", ""),
    )
    min_discount = float(os.getenv("MIN_DISCOUNT_PERCENT", "5"))

    if args.provider == "keepa":
        adapter = KeepaAdapter()
        products = adapter.fetch(load_keepa_items(input_path))
    elif args.provider == "asin":
        adapter = AsinDevAdapter()
        products = adapter.fetch(load_keepa_items(input_path))
    elif args.provider == "scavio":
        adapter = ScavioAdapter()
        products = adapter.fetch(load_keepa_items(input_path))
    else:
        products = load_products(input_path)

    process_products(products, storage, notifier, min_discount)


if __name__ == "__main__":
    main()
