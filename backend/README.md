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

## Database

This application uses PostgreSQL with SQLAlchemy ORM and Flask-Migrate for migrations.

### Database Models

- **User**: User authentication and file ownership
  - Fields: id, username, email, password_hash, created_at, updated_at, is_active
  - Relationships: files (one-to-many)

- **File**: File metadata and tracking
  - Fields: id, filename, original_filename, file_path, file_size, mime_type, file_hash
  - Fields: user_id, description, tags, uploaded_at, updated_at, last_accessed_at
  - Fields: is_public, is_deleted, deleted_at, download_count
  - Relationships: owner (many-to-one with User), shares (one-to-many with FileShare)

- **FileShare**: File sharing with users or public links
  - Fields: id, file_id, share_token, shared_with_user_id
  - Fields: can_download, can_view, expires_at, created_at, accessed_count, last_accessed_at, is_active
  - Relationships: file (many-to-one), shared_with_user (many-to-one with User)

### Database Migrations

Initialize migrations (first time only):
```bash
flask db init
```

Create a new migration:
```bash
flask db migrate -m "Description of changes"
```

Apply migrations:
```bash
flask db upgrade
```

Rollback migration:
```bash
flask db downgrade
```

### Development Database Setup

Using Docker Compose (recommended):
```bash
docker-compose up db
```

Or install PostgreSQL locally and create database:
```bash
createdb filesvc
```

## API Endpoints

- `GET /` - Root endpoint, returns API info
- `GET /api/health` - Health check endpoint (includes database status)
- `GET /api/db/init` - Initialize database tables (development only)

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