# PatentIQ

PatentIQ is a patent analysis and intelligence platform built with Astro 5 and Flask.

## Tech Stack

- **Frontend:** Astro 5 (Static Site Generator)
- **Backend:** Flask (Python)
- **Deployment:** AWS ECS (planned)

## Project Structure

```
.├── frontend/          # Astro 5 frontend application
│   ├── src/          # Source code
│   ├── public/       # Static assets
│   └── Dockerfile    # Frontend container
├── backend/          # Flask backend API
│   ├── app.py        # Main application
│   ├── requirements.txt
│   └── Dockerfile    # Backend container
├── docker-compose.yml # Local development
└── .github/workflows/ # CI/CD pipelines
```

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- Docker (optional)

### Local Development

1. **Start the backend:**
   cd backend && pip install -r requirements.txt && python app.py
   Backend runs at http://localhost:5000

2. **Start the frontend:**
   cd frontend && npm install && npm start
   Frontend runs at http://localhost:4321

### Docker Development

   docker-compose up --build

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| / | GET | Root - Hello World |
| /health | GET | Health check |

## Deployment

See CLAUDE.md for AWS ECS deployment steps.

## License

MIT
