# AmazonDealHunter

Amazon product price tracking, price-drop detection and Telegram notifications.

## Features

- Asin.dev adapter with a free daily tracking tier (up to 50 products)
- Optional Keepa adapter for supported marketplaces
- SQLite price history and local price-drop comparison
- Optional Telegram notifications
- Docker image and scheduled GitHub Actions workflow
- Demo mode for local development

## Recommended live mode: Asin.dev free tier

Asin.dev documents a free tier for up to 50 products checked daily. Confirming an account email adds 1,500 trial credits. Each scheduled product check uses one credit; the provider manages the daily check schedule. The API's documented marketplace list does **not** include Amazon Turkey.

1. Create an account at https://www.asin.dev and confirm your email.
2. Create an API key in the dashboard.
3. Copy `.env.example` to `.env` and set `ASIN_API_KEY`.
4. Add products to `data/products.asin.example.json`:

```json
[
  { "asin": "B09DFCB66S", "marketplace": "com" },
  { "asin": "YOUR_ASIN_HERE", "marketplace": "de" }
]
```

Supported marketplace codes: `com`, `co.uk`, `de`, `fr`, `it`, `es`, `ca`, `co.jp`, `com.br`, `com.mx`, `in`.

Run a live check:

```bash
python -m src.main --provider asin
```

The first run registers products in your Asin.dev watchlist and requests an initial check. Later runs read the latest tracked prices. Asin.dev performs recurring daily checks on its side; the GitHub Actions workflow reads the latest values every six hours and compares them with the local SQLite history to send Telegram drop alerts.

The free tier is limited to 50 tracked products and daily checks. Faster checks and larger watchlists require a paid plan or credits. See the provider's current limits and terms before relying on it for production.

## Optional live mode: Keepa

Keepa remains available as a paid alternative. Set `KEEPA_API_KEY`, then run:

```bash
python -m src.main --provider keepa
```

Keepa supports `us`, `uk`, `de`, `fr`, `jp`, `ca`, `it`, `es`, `in`, `mx`, and `br`. It does not currently list Amazon.com.tr.

## GitHub Actions automation

The workflow at `.github/workflows/price-check.yml` runs every six hours (UTC) and can also be started manually from the **Actions** tab.

Add these repository secrets under **Settings → Secrets and variables → Actions**:

- `ASIN_API_KEY` (required for the default live workflow)
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
| `ASIN_API_KEY` | Asin live mode | Asin.dev API key |
| `KEEPA_API_KEY` | Keepa live mode | Keepa API key |
| `TELEGRAM_BOT_TOKEN` | No | Telegram bot token |
| `TELEGRAM_CHAT_ID` | No | Telegram destination |
| `MIN_DISCOUNT_PERCENT` | No | Minimum discount to notify (default: 5) |
| `DATABASE_PATH` | No | SQLite database path |

Without Telegram credentials, alerts are printed to the console.

## Limitations and responsible use

- Amazon Turkey is not in the documented marketplace list for either current provider. A separate provider with explicit Amazon.com.tr coverage and suitable terms is needed.
- Live price checks depend on the provider's coverage, rate limits, account status and API availability.
- This project does not bypass CAPTCHAs, logins, rate limits or access controls.
- Price history starts accumulating after the product is first tracked by this project/provider; it is not a guarantee of complete historical data.
- Telegram alerts are generated when this workflow compares a newly observed provider price against the previous locally stored price.

## License

MIT
