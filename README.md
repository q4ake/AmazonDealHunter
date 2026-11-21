# AmazonDealHunter

Amazon product price tracking, price-drop detection and Telegram notifications.

## Features

- Scavio adapter for Amazon Turkey (amazon.com.tr), Turkish titles and TRY prices
- Optional Asin.dev adapter for its supported non-Turkey marketplaces
- Optional Keepa adapter for its supported non-Turkey marketplaces
- SQLite price history and local price-drop comparison
- Optional Telegram notifications
- Docker image and scheduled GitHub Actions workflow
- Demo mode for local development

## Recommended live mode: Scavio (Amazon Turkey)

Scavio documents Amazon Turkey support using `country: "tr"` and `language: "TR"`. Its product-detail endpoint accepts an ASIN and returns normalized product data including current price, currency, title and URL. The provider currently documents 1 credit per successful search, product-detail or offers call, and 50 free credits for new accounts. Confirm current pricing and limits in your dashboard before relying on it.

1. Create an account at https://www.scavio.dev/tr/amazon-api.
2. Create an API key in the Scavio dashboard.
3. Copy `.env.example` to `.env` and set `SCAVIO_API_KEY`.
4. Add products to `data/products.scavio.example.json`:

```json
[
  { "asin": "B0CDMB5ZQW", "country": "tr", "language": "TR" },
  { "asin": "YOUR_ASIN_HERE", "country": "tr", "language": "TR" }
]
```

Run a live check:

```bash
python -m src.main --provider scavio
```

Each product detail lookup costs one Scavio credit according to its documentation. The first successful run creates a local price-history record; later runs compare the newly fetched TRY price with the previous one. Without Telegram credentials, notifications are printed to the console.

## Optional live mode: Asin.dev

Asin.dev can track products on its supported marketplaces, but its documented list does not include Amazon Turkey. Set `ASIN_API_KEY` and run:

```bash
python -m src.main --provider asin
```

## Optional live mode: Keepa

Keepa remains available as a paid alternative for supported marketplaces. Set `KEEPA_API_KEY`, then run:

```bash
python -m src.main --provider keepa
```

Keepa does not currently list Amazon.com.tr.

## GitHub Actions automation

The workflow at `.github/workflows/price-check.yml` runs every six hours (UTC) and can also be started manually from the **Actions** tab.

Add these repository secrets under **Settings → Secrets and variables → Actions**:

- `SCAVIO_API_KEY` (required for the default Amazon Turkey workflow)
- `TELEGRAM_BOT_TOKEN` (optional)
- `TELEGRAM_CHAT_ID` (optional)

Optionally set the repository variable `MIN_DISCOUNT_PERCENT`; the default is 5.

GitHub-hosted runners are ephemeral. The workflow restores and saves the SQLite price-history cache between runs. Scheduled workflow starts can be delayed during high load, and public-repository schedules may be disabled after extended inactivity.

## Docker

Build and run one check:

```bash
docker build -t amazon-deal-hunter .
docker run --rm --env-file .env -v "$PWD/data:/app/data" amazon-deal-hunter
```

The container performs one check and exits. Docker alone does not schedule recurring runs; use GitHub Actions or an external scheduler.

## Demo mode

No API key is needed:

```bash
python -m src.main --provider demo
```

It reads `data/products.example.json`. Change the sample price and run it again to test price-drop detection.

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `SCAVIO_API_KEY` | Scavio live mode | Scavio API key for Amazon Turkey |
| `ASIN_API_KEY` | Asin.dev live mode | Asin.dev API key |
| `KEEPA_API_KEY` | Keepa live mode | Keepa API key |
| `TELEGRAM_BOT_TOKEN` | No | Telegram bot token |
| `TELEGRAM_CHAT_ID` | No | Telegram destination |
| `MIN_DISCOUNT_PERCENT` | No | Minimum discount to notify (default: 5) |
| `DATABASE_PATH` | No | SQLite database path |

Without Telegram credentials, alerts are printed to the console.

## Limitations and responsible use

- Live price checks depend on the provider's coverage, rate limits, account status and API availability.
- Scavio's documented product endpoint is used for current product price; price history for this project starts accumulating locally after the first successful run.
- This project does not bypass CAPTCHAs, logins, rate limits or access controls.
- Check each provider's current terms and pricing before production use.

## License

MIT
