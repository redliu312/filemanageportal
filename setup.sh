#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up Full Stack Application...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create environment files if they don't exist
echo -e "${BLUE}Creating environment files...${NC}"

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo -e "${GREEN}Created backend/.env${NC}"
else
    echo -e "${BLUE}backend/.env already exists${NC}"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
    echo -e "${GREEN}Created frontend/.env.local${NC}"
else
    echo -e "${BLUE}frontend/.env.local already exists${NC}"
fi

# Build and start Docker containers
echo -e "${BLUE}Building Docker containers...${NC}"
docker-compose build

echo -e "${BLUE}Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to start...${NC}"
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Services are running!${NC}"
    echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
    echo -e "${GREEN}Backend API: http://localhost:8000${NC}"
    echo -e "${BLUE}To view logs: docker-compose logs -f${NC}"
    echo -e "${BLUE}To stop services: docker-compose down${NC}"
else
    echo -e "${RED}Failed to start services. Check logs with: docker-compose logs${NC}"
    exit 1
fi