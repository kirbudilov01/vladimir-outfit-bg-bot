# Outfit Background Transfer Bot

Telegram bot for a repeatable product workflow: keep one approved background and move clothing/product photos from different source images onto it.

## What is included

- `/start` help flow.
- Admin `/set_background` mode: send one image and it becomes the default background.
- Any user can send source photos and receive a composited result.
- Local processing with `rembg` + Pillow. No paid image API is required for the base workflow.
- SQLite job history.
- Docker and docker-compose setup.

## Quick start

```bash
cp .env.example .env
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

For production:

```bash
docker compose up -d --build
```

## Environment

- `BOT_TOKEN` is required.
- `ADMIN_IDS` is a comma-separated list of Telegram user ids.
- `BACKGROUND_PATH` points to the approved background image.

## Workflow

1. Admin sends `/set_background`.
2. Admin sends the fixed background image.
3. Operators send source images with clothing/product.
4. Bot removes the source background, fits the object into the configured placement area, and returns the final image.

The default placement is centered and conservative. Change `PLACEMENT_WIDTH_RATIO`, `PLACEMENT_HEIGHT_RATIO`, and `PLACEMENT_BOTTOM_MARGIN_RATIO` in `.env` for the exact catalog template.

