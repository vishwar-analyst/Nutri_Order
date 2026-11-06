# NutriOrder AI — Project Status

**Last Updated:** 2026-11-06  
**Project Status:** Active Development – Functional Prototype

This document describes the currently implemented features, local execution instructions, test results, and known limitations of NutriOrder AI.

The application is a Tamil Nadu-focused restaurant menu, ordering demo, and food-discovery platform built with HTML, CSS, JavaScript, Flask, and SQLite.

---

## 1. Implementation Status

### Backend & Database
- Flask REST API implemented.
- SQLite database initialization and automatic seeding.
- Additive database schema updates.
- Food catalog and restaurant reference data management.
- Server-side food ID and price validation.
- API health-check endpoint.

### Frontend
- Static HTML, CSS, and JavaScript architecture.
- Home and restaurant menu pages.
- Menu search and filtering.
- Category, dietary preference, and budget filters.
- Food sorting and item details.
- Browser-local shopping cart.
- Customer order submission and order history.
- Registration and sign-in pages.
- NutriBot and NutriMatch interfaces.

### NutriBot – AI Food Assistant
- Local retrieval using live SQLite menu data.
- Curated Markdown and TXT knowledge document retrieval.
- Structured food and health-suitability responses.
- Optional Google Gemini integration.
- Optional Chroma semantic retrieval.
- Evidence-based responses with unknown information handled conservatively.
- Baseline keyword retrieval works without external AI services.

### NutriMatch – Recommendation Engine
- Deterministic weighted preference matching.
- Goal, nutrition, cuisine, taste, budget, and meal preferences.
- Allergy and dietary filtering.
- Verification handling for uncertain food records.
- Request-scoped preference selections.

### Customer Authentication & Orders
- Customer registration and sign-in.
- Password hashing using Werkzeug.
- Session handling with HTTP-only and SameSite cookies.
- Password reset endpoints.
- Optional SMTP-based reset email delivery.
- Customer order submission and history.
- Owner/admin order routes.
- Server-side order validation against current database prices.
- Pending and unavailable food items blocked from ordering.

### Food Catalog & Images
- 16 seeded sample food offers.
- 55 pending traditional food references.
- 16 local representative food photos under `images/`.
- Fallback illustrations for pending dishes.
- Image verification status maintained in records.

**Important:** Pending dishes do not have confirmed prices, nutrition information, or availability. Local photos are illustrative and are not verified restaurant photography.

---

## 2. Testing Status

<badge color="success">37 tests passed</badge>

The integration and business-rule test suite was executed during the 2026-11-06 status review.

**Test command:**

```bash
python -m unittest discover -s tests -v
```

Coverage includes:
- NutriBot health-related response behavior.
- NutriMatch filtering and scoring.
- Flask API routes.
- Tamil food catalog business rules.

Test results represent the status review and should be revalidated after code changes.

---

## 3. Local Execution

### Requirements
- Python 3.10+
- pip
- Git (recommended)
- VS Code (recommended)

### Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Start Backend

```bash
python backend/app.py
```

Default API address:

`http://127.0.0.1:5000`

### Start Frontend

Open a second terminal from the project root:

```bash
python -m http.server 8000
```

### Open Application

`http://localhost:8000/frontend/index.html`

### API Health Check

`http://127.0.0.1:5000/api/test`

The backend automatically initializes and seeds the default root-level `nutriorder.db` database.

Set `NUTRIORDER_DB` to use another database file.

See `README.md` for optional environment variables and Gemini/SMTP configuration.

---

## 4. Local Demo Accounts

The following seed accounts are intended exclusively for local testing.

| Role | Username | Email |
|---|---|---|
| Customer | `customer` | `customer@nutriorder.local` |
| Owner | `bakery` | `owner@nutriorder.local` |

**Demo password:** `1234`

**Security warning:** Never use these credentials for real accounts or expose them in a public deployment.

---

## 5. Known Limitations

### Security & Authentication
- Authentication and authorization require production security review.
- Session-secret defaults require hardening.
- Email verification is not implemented.
- Password reset email delivery requires SMTP configuration.
- Production deployment settings require additional security measures.

### Restaurant Operations
- Production payment processing is not implemented.
- Live food inventory is not implemented.
- Full menu administration remains incomplete.
- Owner/admin analytics are incomplete.
- Subscription functionality is incomplete.
- Production deployment and operations are not complete.

### Food Data Accuracy
- Seeded calorie and macronutrient values are estimates.
- Pending traditional dishes have unknown prices and nutrition values.
- Missing nutritional values must not be interpreted as zero.
- Food images are representative, not confirmed exact-dish restaurant photos.
- Recipes, ingredients, allergens, cross-contact, and availability require restaurant confirmation.

### AI & Health Safety
- NutriBot provides general informational responses.
- NutriMatch provides preference-based recommendations.
- Neither system diagnoses medical conditions or prescribes diets.
- Neither system calculates clinical nutritional targets.
- Allergy safety cannot be guaranteed.

---

## 6. Future Development Priorities

| Priority | Planned Enhancement |
|---|---|
| High | Verify traditional Tamil food catalog data |
| High | Improve NutriBot RAG retrieval and response evaluation |
| High | Production authentication and security hardening |
| Medium | Restaurant owner/admin dashboard |
| Medium | Live inventory management |
| Medium | Payment gateway integration |
| Medium | Restaurant analytics and reporting |
| Future | Advanced personalized recommendations |
| Future | Production deployment |

---

## 7. Project Information

| Category | Details |
|---|---|
| Project | NutriOrder AI |
| Domain | Artificial Intelligence & Data Science |
| Application | Restaurant Menu, Ordering & Food Discovery |
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| Database | SQLite |
| AI | Google Gemini (Optional) |
| RAG | Local Retrieval + Optional Chroma |
| Development Stage | Functional Prototype |
| Last Status Review | 2026-11-06 |

---

**Development Note:** NutriOrder AI is an evolving prototype. Features marked as implemented are available in the current reviewed codebase, while future enhancements and incomplete production capabilities are not represented as completed features.
