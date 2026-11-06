# NutriOrder AI — Project Status

**Status snapshot:** 2026-11-06. This file describes implemented prototype behavior; server availability is temporary and depends on running the local commands below.

## Implemented

- Flask API with SQLite initialization, additive schema updates, and seeded restaurant/reference food data.
- Static customer pages for home, menu, NutriBot, NutriMatch, registration/sign-in, cart, and orders.
- Menu search, category/diet/budget filters, sorting, item details, and 16 local representative photos in `images/`. Photos are not marked restaurant-verified. Pending catalog dishes intentionally have no specific photo, confirmed price, nutrition, or availability.
- NutriBot local retrieval over the live SQLite menu and curated documents; structured menu/health responses; optional Gemini responses and optional Chroma semantic retrieval.
- Deterministic NutriMatch scoring with allergy/dietary filters and an explicit verification path for uncertain records.
- Customer registration, sign-in, session, password reset, order submission/history, and owner/admin order routes. Order submission checks database prices and blocks pending/unavailable items.
- Test suite: 37 tests passed with `python -m unittest discover -s tests -v` during this status review.

## Run locally

From the project root, install requirements with `python -m pip install -r requirements.txt`. Start the backend with `python backend/app.py`, then in a second terminal run `python -m http.server 8000`. Open `http://localhost:8000/frontend/index.html`. The API health check is `http://127.0.0.1:5000/api/test`.

The API initializes/seeds the default root-level `nutriorder.db` at startup. Set `NUTRIORDER_DB` to use another database file. Python 3.10+ is required. See [README.md](README.md) for optional environment variables and Gemini/SMTP setup.

## Demo accounts

Local-only seed accounts:

- Customer: `customer` or `customer@nutriorder.local` / `1234`
- Owner: `bakery` or `owner@nutriorder.local` / `1234`

Never reuse these credentials for real accounts or expose the demo publicly.

## Known limitations and safety

- This is not production-ready. Authentication, authorization, session-secret defaults, reset delivery, and deployment settings need a security review and hardening. Password hashing and HTTP-only/same-site cookies are implemented, but registration does not verify email. Reset links are delivered only when SMTP is configured.
- No production payment processing or live inventory is implemented. Full menu administration, owner/admin analytics, subscriptions, and deployment operations remain incomplete.
- Seeded calories/macros are estimates. Reference dishes have unknown pricing and nutrition; missing values must not be interpreted as zero.
- Local dish photos are illustrative, not restaurant-confirmed exact-dish photos. Confirm recipes, ingredients, allergens, cross-contact, and availability with restaurant staff.
- NutriBot and NutriMatch provide general informational features only; neither diagnoses, prescribes, calculates clinical targets, nor guarantees that food is allergy-safe.

