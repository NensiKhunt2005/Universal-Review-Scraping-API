# Universal Review Scraping API

A production-ready microservice built with **FastAPI**, **Selenium**, and **Pydantic** to reliably extract textual product reviews from supported e-commerce websites utilizing the Strategy Design Pattern.

## 🚀 Features
- **Strictly Data:** Extracts *only* the review text, ignoring prices, metadata, products, and ads.
- **Clean Architecture:** Built natively with decoupled `Scraping`, `Cleaning`, and `Exporting` layers.
- **Dynamic Configuration:** Controlled by `config/settings.yaml` preventing hardcoded anomalies.
- **Deduplication:** Internal engines utilizing sets for exact and case-insensitive matches.
- **Exporting Options:** Native `SQLite`, `JSON`, and `CSV` exporters.
- **Headless & Concurrent:** Runs seamlessly on cloud servers utilizing headless Chrome containers.

## 📁 Repository Structure
```
├── config/              # Scraper configurations & HTML selectors
├── exports/             # Default mounted output volume for SQLite/JSON/CSV
├── src/                 
│   ├── api/             # FastAPI routers & endpoint orchestration
│   ├── core/            # Logging, settings parser, exceptions
│   ├── models/          # Pydantic schema validation for request/responses
│   ├── scrapers/        # Selenium strategy implementations (`BaseScraper`)
│   ├── services/        # Deduplication & NLP HTML stripping logic
│   └── storage/         # DB/File storage adapters
├── tests/               # PyTest integration and unit mocks
├── .github/workflows/   # CI/CD pipelines
├── docker-compose.yml   # Multi-container local execution
└── Dockerfile           # Chrome-equipped production image
```

## 🛠️ Usage (Local Installation)

1. Set up the virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run the application:
```bash
python src/main.py
```
> Explore the `Swagger UI` automatically at: `http://localhost:8000/docs`

## 🐳 Usage (Docker)
Execute the microservice entirely isolated inside a container.
```bash
docker-compose up --build -d
```

## 🧪 Testing
The CI suite mocks standard Selenium drivers preventing active browser popups.
```bash
pytest tests/
black src --check
flake8 src
```

## 🔌 API Examples

**Endpoint:** `POST /api/v1/scrape`

**Payload:**
```json
{
  "url": "https://www.amazon.com/dp/B08P2H15GN",
  "max_pages": 1,
  "drop_emojis": true,
  "remove_duplicates": true
}
```

**Response:**
```json
{
  "website": "AmazonScraper",
  "total_reviews": 6,
  "reviews": [
    "Amazing product.",
    "Worth every penny.",
    "Quality is excellent."
  ]
}
```

## 💡 Future Integrations
This API acts as an internal microservice and can be dynamically hooked to:
- Next.js Dashboards
- Fake Review Classifiers (BERT/Llama)
- Browser Extensions


@terminal: there are many reviews in this given page but it given 0 reviews in return check this issue properly