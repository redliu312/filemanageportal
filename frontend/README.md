# Frontend - Next.js Application

Modern Next.js frontend with TypeScript and Tailwind CSS, configured for Vercel deployment.

## Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.example .env.local
```

3. Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Project Structure

```
frontend/
├── public/             # Static assets
├── src/
│   ├── app/           # App router pages and layouts
│   │   ├── layout.tsx # Root layout
│   │   ├── page.tsx   # Home page
│   │   └── globals.css # Global styles
│   └── components/    # Reusable components (to be added)
├── .env.example       # Environment variables template
├── .eslintrc.json     # ESLint configuration
├── .gitignore         # Git ignore file
├── next.config.js     # Next.js configuration
├── package.json       # Dependencies and scripts
├── postcss.config.js  # PostCSS configuration
├── README.md          # This file
├── tailwind.config.ts # Tailwind CSS configuration
└── tsconfig.json      # TypeScript configuration
```

## Features

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **ESLint** for code quality
- **API Routes** proxy to backend
- **Environment Variables** support
- **Vercel** deployment ready

## Development

### Code Style
- Use ESLint for linting
- Use Prettier for formatting (can be added)
- Follow TypeScript best practices

### API Integration
The application is configured to proxy API requests to the backend:
- `/api/*` routes are forwarded to the Flask backend
- Configure the backend URL in `.env.local`

## Deployment to Vercel

1. Push your code to GitHub
2. Import the project in Vercel
3. Configure environment variables
4. Deploy

The frontend will automatically deploy with each push to the main branch.

## Environment Variables

See `.env.example` for required environment variables:
- `NEXT_PUBLIC_API_URL` - Backend API URL