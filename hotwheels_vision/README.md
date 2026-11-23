# Hot Wheels Vision Bot (scaffold)

A separate experimental module for identifying Hot Wheels / die-cast variants from user-submitted blister or loose-car photos.

## Intended flow

1. Telegram receives an image (Telegram integration is not implemented yet).
2. OpenCV loads the image and prepares crops for the car, wheels, paint and card/blister markings.
3. A vision model compares visible details against a curated reference set.
4. OCR is applied to enlarged crops when a small TH mark or other text is visible.
5. The result reports Regular / STH / Chase as a hypothesis with evidence and uncertainty. It must request another photo when the evidence is insufficient.
6. A later pricing module will compare sold listings; it is not part of this scaffold.

## Current implementation

- `src/image_prep.py` contains basic image loading, bounded cropping and OCR-oriented preprocessing.
- This is image preparation only. It does **not** classify STH/Chase, detect Spectraflame, identify Real Riders, or estimate market value.
- No Telegram bot, vision API, OCR engine, dataset or pricing scraper is wired yet.

## Setup

```bash
python -m pip install -r requirements.txt
```

The module expects a local image path. Do not commit collection photos or API credentials.
