# Full Stack Application - Flask + Next.js

<p align="center">
  <img src="asserts/demo.gif" width="300" alt="Demo animation">
</p>
A modern full-stack application with Python Flask backend and Next.js frontend, designed for deployment on Vercel.
This repo is **co-work with the roo code vs code extension with claude-4.5 llm models**.

## MVP status

| feature | done | Notes |
|------|---------|-------|
| Setup development environment | ✅  | Installed dependencies and configured environment |
| signup, login, logout | ✅  |  |
|  file upload, download, delete, pagination list |  ✅ |  |
|  file upload progress bar | ❌ |  |
|  file metadata modification(file title) | ✅ |  |
|Supabase free tier sql , storage usage|  ✅ |
| backend flask deployed to vercel serverless function  | ❌ |
| frontend next.js deploed to vercel | ❌   |
| vercel and github integration | ❌  |


## trade off and the future enhancmements

1. Simple JWT authentication with localStorage
the token only expired after 24 hours and no refresh mechanisms.

2. soft delete which make the file still occupy the storage spaces

3. no progress bar for file uploads

4. ** the demo still only run on local , not yet to the vercel or other cloud. **


## arcitecture and sequence diagrams

### file upload
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API Client
    participant Backend API
    participant Storage Service
    participant Storage (Local/Supabase)
    participant Database

    User->>Frontend: Select file to upload
    Frontend->>Frontend: Validate file locally
    Frontend->>API Client: Call uploadFile(file)
    API Client->>API Client: Create FormData with file
    API Client->>Backend API: POST /api/files with FormData
    Backend API->>Backend API: Validate file type & size
    Backend API->>Backend API: Generate unique filename
    Backend API->>Storage Service: Upload file
    Storage Service->>Storage (Local/Supabase): Save file
    Storage (Local/Supabase)-->>Storage Service: Return storage path
    Storage Service-->>Backend API: Return storage path
    Backend API->>Database: Create File record
    Database-->>Backend API: Confirm save
    Backend API-->>Frontend: Return file metadata
    Frontend->>Frontend: Update UI with success

```

### login
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant AuthContext
    participant API Client
    participant Backend
    participant Database
    participant JWT

    User->>Frontend: Enter email & password
    Frontend->>AuthContext: Call login(email, password)
    AuthContext->>API Client: api.login(email, password)
    API Client->>Backend: POST /api/auth/login
    Backend->>Database: Query user by email
    Database-->>Backend: Return user record
    Backend->>Backend: Verify password hash
    Backend->>JWT: Generate token with user_id
    JWT-->>Backend: Return signed token
    Backend-->>API Client: Return {user, token}
    API Client-->>AuthContext: Return response
    AuthContext->>AuthContext: Store token in localStorage
    AuthContext->>AuthContext: Update user state
    AuthContext-->>Frontend: Login successful
    Frontend->>Frontend: Redirect to dashboard
```

### logout
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant AuthContext
    participant API Client
    participant Backend

    User->>Frontend: Click logout
    Frontend->>AuthContext: Call logout()
    AuthContext->>AuthContext: Remove token from localStorage
    AuthContext->>AuthContext: Set user to null
    AuthContext->>API Client: api.logout() (optional)
    API Client->>Backend: POST /api/auth/logout
    Backend-->>API Client: Return success message
    AuthContext->>Frontend: Update UI
    Frontend->>Frontend: Redirect to login page
```

### signup
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant AuthContext
    participant API Client
    participant Backend
    participant Database
    participant JWT

    User->>Frontend: Enter email, password, username
    Frontend->>AuthContext: Call signup(email, password, username)
    AuthContext->>API Client: api.signup(email, password, username)
    API Client->>Backend: POST /api/auth/signup
    Backend->>Backend: Validate input data
    Backend->>Backend: Hash password
    Backend->>Database: Create new user
    Database-->>Backend: Return user record
    Backend->>JWT: Generate token with user_id
    JWT-->>Backend: Return signed token
    Backend-->>API Client: Return {user, token}
    API Client-->>AuthContext: Return response
    AuthContext->>AuthContext: Store token in localStorage
    AuthContext->>AuthContext: Update user state
    AuthContext-->>Frontend: Signup successful
    Frontend->>Frontend: Redirect to dashboard
```

### authentication, happens on every flask login required route

```mermaid
sequenceDiagram
    participant Frontend
    participant API Client
    participant Backend
    participant JWT
    participant Database
    participant Route Handler

    Frontend->>API Client: Make API request
    API Client->>API Client: Get token from localStorage
    API Client->>Backend: Request with Authorization: Bearer {token}
    Backend->>Backend: Extract token from header
    Backend->>JWT: Decode & verify token
    JWT-->>Backend: Return payload {user_id, exp, iat}
    Backend->>Database: Get user by user_id
    Database-->>Backend: Return user object
    Backend->>Route Handler: Call handler with user
    Route Handler-->>Backend: Return response
    Backend-->>API Client: Return response
    API Client-->>Frontend: Return data
```

### when the user need to login

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant HomePage
    participant AuthContext
    
    User->>Browser: Visit website
    Browser->>AuthContext: Check localStorage token
    
    alt No token or invalid token
        AuthContext->>HomePage: user = null
        HomePage->>User: Show Login/Signup form
    else Valid token exists
        AuthContext->>HomePage: user = {id, email, username}
        HomePage->>User: Show user info page
    end
    
    opt User clicks Logout
        User->>HomePage: Click Logout
        HomePage->>AuthContext: Clear token
        AuthContext->>HomePage: user = null
        HomePage->>User: Show Login/Signup form
    end

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

### Prerequisites
- Docker and Docker Compose
- Git

### Development with Local PostgreSQL

1. Clone the repository and setup:
```bash
git clone <repository-url>
cd filemanageportal
./setup.sh
```

2. Start all services:
```bash
make docker-up
```

3. Initialize the database:
```bash
make docker-db-init
```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Development with Supabase Backend

1. Create a `.env.production` file in the backend directory:
   ```bash
   cp backend/.env.production.example backend/.env.production
   # Edit the file and add your Supabase credentials
   ```

2. Start services with Supabase:
   ```bash
   make supabase-up
   ```

3. Initialize Supabase database:
   ```bash
   make supabase-db-init
   # Or use the initialization script:
   ./supabase-init.sh
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000 (connected to Supabase)

### Stopping Services

```bash
# Stop local PostgreSQL setup
make docker-down

# Stop Supabase setup
make supabase-down
```

## Available Commands

### Docker Development Commands

**Local PostgreSQL:**
- `make setup` - Initial project setup with Docker
- `make docker-up` - Start all Docker containers
- `make docker-down` - Stop all Docker containers
- `make docker-build` - Rebuild Docker containers
- `make docker-logs` - View container logs
- `make docker-db-init` - Initialize database tables

**Supabase Backend:**
- `make supabase-up` - Start with Supabase backend
- `make supabase-down` - Stop Supabase containers
- `make supabase-db-init` - Initialize Supabase database

**Utilities:**
- `make clean` - Clean build artifacts
- `make test` - Run tests (inside containers)
- `make lint` - Run linters (inside containers)
- `make help` - Show all available commands

## Environment Variables

### Backend Configuration

**For Local PostgreSQL** (docker-compose.yml):
- Environment variables are set in the docker-compose.yml file
- Database URL: `postgresql://postgres:postgres@db:5432/filesvc`
- Backend runs on port 8000 (mapped from container port 5000)

**For Supabase** (docker-compose.supabase.yml):
- Create `backend/.env.production` from `backend/.env.production.example`
- Add your Supabase credentials (DATABASE_URL, SUPABASE_URL, SUPABASE_KEY)
- Storage mode automatically set to Supabase

### Frontend Configuration

Frontend environment is configured in docker-compose files:
- `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Automatically connects to backend on port 8000

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

Run tests inside Docker containers:
```bash
make test
```

This will execute tests for both frontend and backend within their respective containers.

## Troubleshooting

### Port Already in Use
If you see port conflict errors:
```bash
# Check what's using the ports
lsof -i :3000 -i :8000 -i :5432

# Stop any conflicting services
make docker-down
```

### Database Connection Issues
```bash
# Reinitialize the database
make docker-db-init

# Or for Supabase
make supabase-db-init
```

### Container Issues
```bash
# Rebuild containers from scratch
make docker-build
make docker-up
```

