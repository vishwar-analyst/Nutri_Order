# 🍽️ NutriOrder AI

**NutriOrder AI** is a Tamil Nadu-focused restaurant menu, ordering demo, and food-discovery web application built using HTML, CSS, JavaScript, Flask, and SQLite.

The platform combines restaurant menu browsing, customer authentication, cart and order management, AI-powered food assistance, and personalized food recommendations.

It includes:
- **NutriBot:** A RAG-based food assistant that retrieves menu information and answers food-related questions.
- **NutriMatch:** A preference-based recommendation engine that suggests suitable food options.
- **Restaurant Menu:** Browse, search, filter, and explore traditional and modern Tamil Nadu dishes.
- **Order Management:** Add items to a cart, submit orders, and view order history.
- **Customer Accounts:** Registration, sign-in, session management, and password reset functionality.

> **Project Status:** Development prototype. This application is not a production-ready restaurant commerce platform or medical service.

---

## 🚀 Features

### 1. Restaurant Menu & Ordering
- Browse restaurant food items.
- Search and filter by category, dietary preference, and budget.
- Sort menu items and view individual food details.
- Add items to a browser-local shopping cart.
- Submit customer orders and view order history.
- Server-side validation of food IDs and current prices.
- 16 seeded sample food offers and 55 pending traditional-dish references.

**Note:** Pending catalog items cannot be ordered until verified.

### 2. NutriBot – AI Food Assistant
- Retrieves live menu information from SQLite.
- Searches locally stored Markdown and TXT knowledge documents.
- Provides structured food information.
- Offers conservative food-suitability summaries when relevant.
- Supports local retrieval without an external AI API.
- Optional Gemini-powered grounded responses.
- Optional Chroma vector database for semantic retrieval.
- Displays evidence excerpts and treats missing information as unknown.

### 3. NutriMatch – Food Recommendation System
Uses a deterministic weighted preference-matching algorithm.

| Preference | Weight |
|---|---:|
| Goal | 30% |
| Nutrition | 25% |
| Cuisine | 15% |
| Taste | 10% |
| Budget | 10% |
| Meal | 10% |

- Matches food according to user preferences.
- Applies allergy and dietary filters.
- Routes uncertain food items for verification.
- Uses request-scoped preference selections.
- Does not calculate calorie targets using personal measurements.

**Note:** Recommendation scores are not medical or health assessments.

### 4. Customer Authentication
- Customer registration and sign-in.
- Session management.
- Password hashing using Werkzeug.
- HTTP-only and SameSite session cookies.
- Password reset endpoints.
- Optional SMTP-based password reset emails.

**Note:** Email verification is not implemented. Authentication is currently a prototype.

### 5. Food Images
- Local food image assets stored under `images/`.
- Representative images for seeded sample offers.
- Fallback illustrations for pending catalog dishes.
- Image verification status maintained in the database.

Sample images are not confirmed restaurant photography.

---

## 🛠️ Technology Stack

| Component | Technologies |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, Flask |
| Database | SQLite |
| AI Integration | Google Gemini API |
| RAG | Retrieval-Augmented Generation |
| Vector Database | ChromaDB (Optional) |
| Authentication | Werkzeug, Flask Sessions |
| Embeddings | Configurable Gemini embedding model |
| Development Tools | VS Code, Git, GitHub |

---

## 📂 Project Structure

```text
NutriOrder-AI/
│
├── frontend/
│   ├── index.html
│   ├── menu.html
│   ├── chatbot.html
│   ├── recommendation.html
│   ├── login.html
│   └── register.html
│
├── backend/
│   └── app.py
│
├── images/
│
├── js/
├── css/
│
├── docs/
│   └── ARCHITECTURE.md
│
├── rag/
│   └── ingest.py
│
├── tests/
│
├── requirements.txt
├── .env.example
├── PROJECT_OVERVIEW.txt
├── PROJECT_STATUS.md
└── README.md
```

*The structure above highlights the main project components.*

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.10 or above
- pip
- Git
- VS Code (recommended)

### Step 1: Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd NutriOrder-AI
```

### Step 2: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 3: Start the Backend

```bash
python backend/app.py
```

The Flask API runs by default at:

`http://127.0.0.1:5000`

### Step 4: Start the Frontend

Open a second terminal from the project root:

```bash
python -m http.server 8000
```

### Step 5: Open the Application

Visit:

`http://localhost:8000/frontend/index.html`

---

## 🌐 Application Pages

| Page | Local URL |
|---|---|
| Home | `http://localhost:8000/frontend/index.html` |
| Menu | `http://localhost:8000/frontend/menu.html` |
| NutriBot | `http://localhost:8000/frontend/chatbot.html` |
| NutriMatch | `http://localhost:8000/frontend/recommendation.html` |
| Sign In | `http://localhost:8000/frontend/login.html` |
| Register | `http://localhost:8000/frontend/register.html` |

---

## 🤖 Optional AI Configuration

### Gemini API Integration

To enable Gemini-generated responses, configure your API key on the backend.

1. Copy `.env.example` to `.env`.
2. Add your Gemini API key.
3. Restart the Flask backend.

```env
GEMINI_API_KEY=your_api_key_here
```

Never expose API keys in frontend JavaScript or commit `.env` to GitHub.

### Optional Chroma Semantic Retrieval

Build or refresh the vector database index:

```bash
python -m rag.ingest
```

Run this command from the repository root after configuring the required API key.

If Gemini or Chroma is unavailable, the baseline menu, local retrieval, and deterministic recommendation features continue to work.

---

## 🔧 Configuration

The application supports the following environment variables:

| Variable | Purpose |
|---|---|
| `NUTRIORDER_SECRET_KEY` | Flask session security |
| `NUTRIORDER_DB` | SQLite database path |
| `NUTRIORDER_FRONTEND_ORIGIN` | Allowed frontend CORS origins |
| `NUTRIORDER_COOKIE_SECURE` | Secure cookies over HTTPS |
| `GEMINI_API_KEY` | Gemini API authentication |
| `GEMINI_MODEL` | Gemini generation model |
| `GEMINI_EMBEDDING_MODEL` | Embedding model configuration |
| `MAIL_SERVER` | SMTP server |
| `MAIL_PORT` | SMTP port |
| `MAIL_FROM` | Sender email address |
| `MAIL_USERNAME` | SMTP username |
| `MAIL_PASSWORD` | SMTP password |

The database is created, migrated, and seeded automatically when the backend starts.

By default, the application uses the root-level `nutriorder.db` file.

---

## 🧪 Testing

Run the integration and business-rule test suite from the project root:

```bash
python -m unittest discover -s tests -v
```

The test suite covers:

- NutriBot health-related response behavior.
- NutriMatch filtering and scoring.
- Backend API routes.
- Tamil food catalog business rules.

---

## 📚 Documentation

Additional project documentation:

- `PROJECT_OVERVIEW.txt` – Detailed implementation overview.
- `PROJECT_STATUS.md` – Current development status and known limitations.
- `docs/ARCHITECTURE.md` – Long-term system architecture and design.

---

## ⚠️ Limitations & Safety

- This is a development and demonstration project.
- Nutrition values for seeded dishes may be estimates.
- Food recipes, allergens, prices, serving sizes, and availability require restaurant confirmation.
- Sample images are representative, not verified restaurant photographs.
- NutriBot does not diagnose medical conditions or prescribe diets.
- NutriMatch does not guarantee allergy safety.
- Demo accounts must never be used for real accounts or public deployments.
- Email verification is not implemented.
- Payment processing is not implemented.
- Full restaurant owner/admin management and analytics are incomplete.
- Live inventory management is not implemented.
- Production deployment security hardening is still required.

---

## 🔮 Future Enhancements

Potential future improvements include:

- Restaurant owner and admin dashboard.
- Online payment integration.
- Real-time food availability and inventory.
- Verified restaurant food images and nutritional information.
- Improved RAG retrieval and response evaluation.
- Advanced personalized food recommendations.
- Production-ready authentication and deployment.
- Restaurant analytics and sales reporting.

---

## 👨‍💻 Project Information

**Project Name:** NutriOrder AI  
**Domain:** Artificial Intelligence, Data Science & Web Development  
**Application Type:** Restaurant Menu, Ordering & Food Discovery  
**Development Status:** Prototype / Ongoing Development

