# Backend - Flask API

Python Flask backend configured for deployment as Vercel Serverless Functions.

## Setup

### Prerequisites
- Python 3.13
- uv (Python package manager)

### Installation

1. Create virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

3. Copy environment variables:
```bash
cp .env.example .env
```

4. Run the development server:
```bash
python src/app.py
```

The API will be available at http://localhost:5000

## API Endpoints

- `GET /` - Root endpoint, returns API info
- `GET /api/health` - Health check endpoint

## Project Structure

```
backend/
├── api/            # Vercel serverless function entry
│   └── index.py    # Main entry point for Vercel
├── src/            # Source code
│   ├── __init__.py
│   └── app.py      # Flask application
├── tests/          # Test files
├── .env.example    # Environment variables template
├── .gitignore      # Git ignore file
├── .python-version # Python version for pyenv
├── pyproject.toml  # Project configuration
├── README.md       # This file
└── requirements.txt # Python dependencies
```

## Development

### Code Style
- Use Black for code formatting
- Use Flake8 for linting
- Use MyPy for type checking

### Testing
```bash
pytest
```

## Deployment to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

The backend will be deployed as serverless functions at `/api/*` routes.

## Environment Variables

See `.env.example` for required environment variables.

Key variables:
- `FLASK_DEBUG` - Enable Flask debug mode
- `SECRET_KEY` - Flask secret key
- `ALLOWED_ORIGINS` - CORS allowed origins