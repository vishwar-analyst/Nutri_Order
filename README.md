# NutriOrder AI

NutriOrder AI is a local Tamil Nadu restaurant menu, ordering demo, and food-discovery app built with static HTML/CSS/JavaScript, Flask, and SQLite. It includes customer sign-in and registration, a menu/cart/order flow, NutriBot, and NutriMatch. It is a development prototype, not a production commerce or medical service.

## Run locally

Requirements: Python 3.10+ and pip. From the repository root:

1. Install dependencies: `python -m pip install -r requirements.txt`
2. Start the API: `python backend/app.py` (default: `http://127.0.0.1:5000`).
3. In a second terminal, serve the frontend: `python -m http.server 8000`.
4. Open `http://localhost:8000/frontend/index.html`.

The API creates/migrates and seeds the SQLite database on startup. By default it uses the root-level `nutriorder.db`. Set `NUTRIORDER_DB` to a different absolute path, or a path relative to the project root, to use another database. For optional configuration, copy `.env.example` to `.env` and replace the sample secret. Never commit `.env` or put provider keys in browser code.

Useful pages: [Menu](http://localhost:8000/frontend/menu.html), [NutriBot](http://localhost:8000/frontend/chatbot.html), [NutriMatch](http://localhost:8000/frontend/recommendation.html), [Sign in](http://localhost:8000/frontend/login.html), and [Register](http://localhost:8000/frontend/register.html).

## Features

- **Menu and orders:** Search, category/diet/budget filters, sorting, item details, a browser-local cart, customer order submission, and order history. The server validates orderable food IDs and current prices. The demo menu contains 16 seeded sample offers and 55 pending traditional-dish references; pending items cannot be ordered.
- **Local food photos:** Seeded sample offers use image assets under `images/` and are served by the static frontend. These are representative photos, not confirmed restaurant photography; records keep `image_verified` false. Pending catalog dishes intentionally have no dish-specific photos and use the local fallback illustration.
- **NutriBot:** Retrieves live SQLite menu data and local Markdown/TXT knowledge. It provides structured food information and conservative health-suitability summaries when relevant. Without a Gemini key it uses local retrieval and evidence excerpts. With `GEMINI_API_KEY`, Gemini can generate grounded responses; Chroma semantic retrieval is optional and requires building an index. Missing facts remain unknown.
- **NutriMatch:** Deterministic preference matching with fixed weights (goal 30%, nutrition 25%, cuisine 15%, taste 10%, budget 10%, meal 10%). Allergy and dietary rules filter or route uncertain items for verification. Preference selections are request-scoped; personal measurements are not submitted or used to calculate calorie targets. Match scores are not health assessments.
- **Accounts:** Customer registration, sign-in, session handling, and password reset endpoints are implemented. Passwords are hashed and sessions use HTTP-only/same-site cookies, but the authentication remains a prototype; registration does not verify email, and reset emails require SMTP configuration.

See [PROJECT_OVERVIEW.txt](PROJECT_OVERVIEW.txt) for implementation details and [PROJECT_STATUS.md](PROJECT_STATUS.md) for known limitations and the latest local checks. The architecture document describes the longer-term design, not all currently implemented functionality: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Tests

Run the integration and business-rule tests from the project root:

`python -m unittest discover -s tests -v`

The suite covers NutriBot health behavior, NutriMatch filters/scoring, API routes, and the Tamil food catalog.

## Optional Gemini and semantic retrieval

Set `GEMINI_API_KEY` in the backend process environment or local `.env` file to enable Gemini responses. To build or refresh the optional Chroma index, run `python -m rag.ingest` from the repository root after setting the key. Keep credentials server-side. If Gemini or the index is unavailable, baseline menu, local retrieval, and deterministic recommendation features continue to work. Local vector data is not committed.

## Configuration and safety

- `NUTRIORDER_SECRET_KEY`: set a strong random value outside local-only development.
- `NUTRIORDER_DB`: optional SQLite file path.
- `NUTRIORDER_FRONTEND_ORIGIN`: optional comma-separated CORS origins; the defaults allow local ports 8000 and 5500.
- `NUTRIORDER_COOKIE_SECURE=true`: use when serving over HTTPS.
- `GEMINI_API_KEY`, `GEMINI_MODEL`, and `GEMINI_EMBEDDING_MODEL`: optional server-side AI settings.
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_FROM`, `MAIL_USERNAME`, and `MAIL_PASSWORD`: optional password-reset email delivery settings.

Demo accounts are seeded for local testing and must never be used for real accounts or a public deployment. Sample nutrition may be estimated; recipe, allergen, availability, serving, and cross-contact details require restaurant confirmation. NutriBot and NutriMatch do not diagnose, prescribe, or guarantee allergy safety. Payment processing, full owner/admin management and analytics, production deployment hardening, and live inventory are not complete.
