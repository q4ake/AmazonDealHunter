# AmazonDealHunter

Amazon mağazaları için ASIN tabanlı fiyat takibi ve indirim alarmı.

## Features

- Keepa API adapter for supported Amazon marketplaces
- SQLite price history
- Price-drop percentage calculation
- Optional Telegram notifications
- Demo mode for local testing
- Configurable discount threshold

## Live mode (Keepa)

Live mode uses the **Keepa API**. A Keepa API subscription/key is required; API requests consume Keepa tokens according to its plan.

1. Install Python 3.10+ and dependencies:

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and set `KEEPA_API_KEY`. Telegram settings are optional.

3. Add ASINs and marketplace codes to `data/products.keepa.example.json`:

```json
[
  { "asin": "B0EXAMPLE01", "marketplace": "de" },
  { "asin": "B0EXAMPLE02", "marketplace": "us" }
]
```

4. Run:

```bash
python -m src.main --provider keepa
```

Or specify another list:

```bash
python -m src.main --provider keepa --input data/my-products.json
```

Supported marketplace codes: `us`, `uk`, `de`, `fr`, `jp`, `ca`, `it`, `es`, `in`, `mx`, `br`.

**Amazon Turkey note:** Keepa's currently documented marketplace list does not include Amazon.com.tr. The Keepa adapter therefore rejects `marketplace: "tr"` rather than silently returning incorrect data. A separate compliant Turkish data provider is required for Amazon Turkey.

The adapter reads Keepa's current Amazon price first and falls back to the marketplace-new price when the Amazon price is unavailable. Keepa prices are converted from the marketplace's minor currency unit before being stored.

## Automated checks and Docker

The GitHub Actions workflow at `.github/workflows/price-check.yml` runs every 6 hours (UTC) and can also be started manually from the **Actions** tab. It restores and saves the SQLite price-history cache between runs.

Add these repository secrets under **Settings → Secrets and variables → Actions**:

- `KEEPA_API_KEY` (required for live checks)
- `TELEGRAM_BOT_TOKEN` (optional)
- `TELEGRAM_CHAT_ID` (optional)

Optionally set the repository variable `MIN_DISCOUNT_PERCENT`; the default is 5.

The workflow only runs after the repository's default branch contains the workflow file. GitHub may delay scheduled runs during high load, and scheduled workflows in public repositories can be automatically disabled after extended inactivity.

Build and run a one-off Docker check:

```bash
docker build -t amazon-deal-hunter .
docker run --rm --env-file .env -v "$PWD/data:/app/data" amazon-deal-hunter
```

The container performs one price check and exits. Use GitHub Actions cron or an external scheduler for recurring execution; Docker by itself does not keep the check running every few hours.

## Demo mode

Demo mode requires no API key:

```bash
python -m src.main --provider demo
```

It reads `data/products.example.json`. To test a price drop, run it again after changing the example price; the previous value is stored in SQLite.

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `KEEPA_API_KEY` | Live mode | Keepa API key |
| `TELEGRAM_BOT_TOKEN` | No | Telegram bot token |
| `TELEGRAM_CHAT_ID` | No | Telegram destination |
| `MIN_DISCOUNT_PERCENT` | No | Minimum discount to notify (default: 5) |
| `DATABASE_PATH` | No | SQLite database path |

If Telegram credentials are omitted, notifications are printed to the console.

## Limitations and responsible use

- Live marketplace data depends on Keepa coverage, API availability, and the user's token balance.
- The project does not scrape Amazon pages or bypass CAPTCHAs, logins, rate limits, or access controls.
- Price checks are performed when the program is run. A scheduler or always-on worker must be configured separately for recurring checks.
- Keepa's API data may not be instantaneous; consult its documentation for update and token behavior.

## License

MIT
