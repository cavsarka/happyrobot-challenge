# HappyRobot Challenge — Inbound Carrier Sales Automation

An AI-powered inbound carrier sales system built on the HappyRobot platform for Acme Logistics. The system automates the full carrier call workflow — FMCSA verification, load matching, price negotiation, and warm transfer to a sales rep — with a custom analytics dashboard for real-time operational visibility.

## Live Deployment

| Resource | URL |
|----------|-----|
| Dashboard + API | https://chinmay-happyrobot-challenge.fly.dev |
| API Docs | https://chinmay-happyrobot-challenge.fly.dev/docs |

## Architecture

- **AI Agent** — HappyRobot platform (two-module flow: verification + load matching, then pitching + negotiation)
- **Backend** — FastAPI (Python 3.11)
- **Database** — PostgreSQL on Supabase
- **Frontend** — React + Vite + Recharts + Leaflet
- **Deployment** — Fly.io, containerized with Docker

## Project Structure

```
happyrobot-challenge/
├── backend/
│   ├── main.py          # FastAPI app, all endpoints
│   ├── models.py        # SQLAlchemy models (Load, Call, Booking)
│   ├── database.py      # DB connection
│   └── reset_db.py      # DB init and seed script
├── frontend/
│   ├── src/
│   │   ├── components/  # Dashboard screens and UI components
│   │   └── main.jsx
│   └── dist/            # Built frontend (served by FastAPI)
├── Dockerfile
├── fly.toml
└── requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and fill in the following:

```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
API_KEY=your_api_key_here
FMCSA_API_KEY=your_fmcsa_api_key_here
```

## Running Locally with Docker

```bash
# 1. Clone the repo
git clone https://github.com/chinmayavsarkar/happyrobot-challenge
cd happyrobot-challenge

# 2. Set up environment
cp .env.example .env
# Fill in your credentials in .env

# 3. Build and run
docker build -t happyrobot-challenge .
docker run -p 8080:8080 --env-file .env happyrobot-challenge

# 4. Initialize the database
docker exec $(docker ps -q) python backend/reset_db.py

# 5. Open http://localhost:8080
```

## Running Locally without Docker

```bash
# Backend
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Deploying to Fly.io

```bash
# Install Fly CLI: https://fly.io/docs/hands-on/install-flyctl/

fly auth login
fly secrets set DATABASE_URL=... API_KEY=... FMCSA_API_KEY=...
fly deploy

# Initialize database
fly ssh console -C "python backend/reset_db.py"
```

## API Authentication

All endpoints require an `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key" \
  https://chinmay-happyrobot-challenge.fly.dev/api/v1/dashboard/summary
```

## Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/calls/complete` | HappyRobot webhook — receives call data on completion |
| GET | `/api/v1/loads/search` | Load search with origin, destination, equipment type |
| GET | `/api/v1/carriers/verify/{mc_number}` | FMCSA carrier verification |
| GET | `/api/v1/dashboard/summary` | Executive overview metrics |
| GET | `/api/v1/dashboard/calls` | Paginated call log with filters |
| GET | `/api/v1/dashboard/loads/map` | Booked loads with geocoordinates for map |
| GET | `/api/v1/dashboard/carriers` | Carrier CRM data |
