# Full Stack Application - Flask + Next.js

A modern full-stack application with Python Flask backend and Next.js frontend, designed for deployment on Vercel.

## Project Structure

```
.
├── backend/                 # Flask backend application
│   ├── api/                # API endpoints (Vercel serverless functions)
│   ├── src/                # Source code
│   ├── tests/              # Backend tests
│   ├── .env.example        # Backend environment template
│   ├── .gitignore          # Backend gitignore
│   ├── .python-version     # Python version specification
│   ├── pyproject.toml      # Python project configuration
│   ├── README.md           # Backend documentation
│   ├── requirements.txt    # Python dependencies
│   └── vercel.json         # Vercel configuration
├── frontend/               # Next.js frontend application
│   ├── public/             # Static assets
│   ├── src/                # Source code
│   │   └── app/           # App router
│   │       ├── globals.css # Global styles
│   │       ├── layout.tsx  # Root layout
│   │       └── page.tsx    # Home page
│   ├── .env.example        # Frontend environment template
│   ├── .eslintrc.json      # ESLint configuration
│   ├── .gitignore          # Frontend gitignore
│   ├── next.config.js      # Next.js configuration
│   ├── package.json        # Node dependencies
│   ├── postcss.config.js   # PostCSS configuration
│   ├── README.md           # Frontend documentation
│   ├── tailwind.config.ts  # Tailwind CSS configuration
│   ├── tsconfig.json       # TypeScript configuration
│   └── vercel.json         # Vercel configuration
├── docker/                 # Docker configuration files
│   ├── backend.Dockerfile  # Backend Docker image
│   └── frontend.Dockerfile # Frontend Docker image
├── .dockerignore           # Docker ignore file
├── .gitignore              # Root gitignore
├── dev.sh                  # Development script (no Docker)
├── docker-compose.yml      # Docker Compose configuration
├── Makefile                # Common development tasks
├── README.md               # This file
└── setup.sh                # Initial setup script
```

## Tech Stack

### Backend
- Python 3.13
- Flask
- uv (Python package manager)
- Vercel Serverless Functions

### Frontend
- Next.js 14+
- React
- TypeScript
- Tailwind CSS

### Development
- Docker & Docker Compose
- Hot reloading for both frontend and backend

## Quick Start

### Using Make (Recommended)
```bash
# Initial setup with Docker
make setup

# Run development servers locally (no Docker)
make dev

# Docker commands
make docker-up      # Start containers
make docker-down    # Stop containers
make docker-build   # Rebuild containers
make docker-logs    # View logs
```

### Using Scripts
```bash
# Setup with Docker
./setup.sh

# Development without Docker
./dev.sh
```

### Manual Setup

#### Prerequisites
- Docker and Docker Compose (for containerized development)
- Node.js 18+ (for local frontend development)
- Python 3.13 (for local backend development)
- uv (Python package manager)

#### Local Development with Docker

1. Clone the repository
2. Run the setup script:
   ```bash
   ./setup.sh
   # or
   make setup
   ```

3. Access the applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

#### Local Development without Docker

1. Run the development script:
   ```bash
   ./dev.sh
   # or
   make dev
   ```

2. Or manually set up each service:

   **Backend:**
   ```bash
   cd backend
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   cp .env.example .env
   python src/app.py
   ```

   **Frontend:**
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   npm run dev
   ```

## Available Commands

### Make Commands
- `make help` - Show available commands
- `make setup` - Initial project setup
- `make dev` - Run development servers
- `make docker-up` - Start Docker containers
- `make docker-down` - Stop Docker containers
- `make docker-build` - Rebuild Docker containers
- `make docker-logs` - View Docker logs
- `make clean` - Clean build artifacts
- `make test` - Run tests
- `make lint` - Run linters

### NPM Scripts (Frontend)
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript checking

## Environment Variables

### Backend (.env)
```bash
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
PORT=5000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
NODE_ENV=development
```

## Deployment

Both frontend and backend are configured for deployment on Vercel.

### Backend Deployment
1. Deploy to Vercel:
   ```bash
   cd backend
   vercel
   ```

2. Set environment variables in Vercel dashboard

### Frontend Deployment
1. Deploy to Vercel:
   ```bash
   cd frontend
   vercel
   ```

2. Set the `NEXT_PUBLIC_API_URL` to your backend URL

## Testing

Run tests for both frontend and backend:
```bash
make test
```

Or individually:
```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && npm test
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.