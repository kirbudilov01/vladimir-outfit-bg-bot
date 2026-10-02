# Outfit Background Transfer Bot

Telegram bot for a repeatable production workflow: keep one approved background and move clothing/product photos from different source images onto it.

## Current Product State

This repo is ready to run as a working MVP after you add a real Telegram bot token.

Implemented:

- Telegram onboarding and persistent keyboard.
- Admin-only background setup.
- `/status`, `/help`, `/cancel` support.
- Operator flow: send source photo, receive composited result.
- Local background removal with `rembg`.
- Pillow composition with placement controls and soft shadow.
- SQLite job history.
- Job stats in `/status`.
- File-size guardrail.
- Docker healthcheck.
- GitHub Actions CI.
- Docker and docker-compose deployment.
- No paid AI API required for the base workflow.

Not included yet by design:

- Real Telegram bot token.
- Human visual QA rules for each product category.
- Batch album processing.
- Manual crop/position editor.

## External Services Needed

Required:

- Telegram BotFather bot token: `BOT_TOKEN`.
- A server/VPS or any Docker host.

Required model dependency:

- `rembg` uses an open model for background removal.
- On first run it may download model files. Make sure the server has internet access during first processing.

Not required:

- OpenAI API key.
- Payment provider.
- Mini app hosting.

## Quick Start

```bash
cp .env.example .env
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

Production:

```bash
docker compose up -d --build
```

## Environment

```bash
BOT_TOKEN=123456:telegram-bot-token
ADMIN_IDS=123456789
DATABASE_PATH=./data/outfit_bg.sqlite3
BACKGROUND_PATH=./data/background.jpg
PLACEMENT_WIDTH_RATIO=0.72
PLACEMENT_HEIGHT_RATIO=0.82
PLACEMENT_BOTTOM_MARGIN_RATIO=0.04
MAX_PHOTO_MB=20
OUTPUT_QUALITY=95
```

## Admin Flow

1. Open `/start`.
2. Press `Задать фон` or send `/set_background`.
3. Send the approved background image.
4. Check `/status`.

## Operator Flow

1. Send a clear source photo of the item.
2. Wait while the bot removes the original background.
3. Receive the final image on the fixed background.
4. Send the next source photo.

## Input Quality Rules

Best results:

- object is visible fully;
- background is not the same color as the item;
- good light and sharp focus;
- no hands covering important parts;
- no heavy shadows crossing the item.

Weak results usually come from:

- transparent, white-on-white, black-on-black, or fuzzy items;
- cropped product edges;
- mirrors, reflections, or clutter behind the item.

## Tuning

If the item is too large or small, adjust:

- `PLACEMENT_WIDTH_RATIO`;
- `PLACEMENT_HEIGHT_RATIO`;
- `PLACEMENT_BOTTOM_MARGIN_RATIO`.

The default setup is conservative and centered. For a real catalog workflow, tune these values using 20-30 representative photos and one final approved background.

## Verification

Local syntax check:

```bash
python -m compileall app tests
```

Unit tests:

```bash
pytest -q
```

Docker healthcheck:

```bash
python -m app.healthcheck
```

CI runs compile and tests on every push through GitHub Actions.

## 100/100 Launch Checklist

The code is complete for handoff. To call the live product 100/100, complete these external steps:

1. Create a BotFather bot and set `BOT_TOKEN`.
2. Put admin Telegram ids into `ADMIN_IDS`.
3. Start the bot on the production server.
4. Run `/start`, `/status`, `Задать фон`.
5. Upload the final approved background.
6. Process 20-30 real source photos.
7. Tune placement ratios in `.env`.
8. Restart and confirm `/status` still sees the background and job stats.
9. Give operators the source-photo quality rules above.
