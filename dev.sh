#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  File Management Portal - Docker Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}This project uses Docker for local development.${NC}"
echo -e "${YELLOW}Please use one of the following commands:${NC}"
echo ""
echo -e "${GREEN}For local development with PostgreSQL:${NC}"
echo -e "  ${BLUE}make docker-up${NC}        - Start all services"
echo -e "  ${BLUE}make docker-db-init${NC}   - Initialize database"
echo -e "  ${BLUE}make docker-down${NC}      - Stop all services"
echo ""
echo -e "${GREEN}For development with Supabase:${NC}"
echo -e "  ${BLUE}make supabase-up${NC}      - Start with Supabase backend"
echo -e "  ${BLUE}make supabase-db-init${NC} - Initialize Supabase database"
echo -e "  ${BLUE}make supabase-down${NC}    - Stop Supabase services"
echo ""
echo -e "${GREEN}Other useful commands:${NC}"
echo -e "  ${BLUE}make docker-logs${NC}      - View container logs"
echo -e "  ${BLUE}make docker-build${NC}     - Rebuild containers"
echo -e "  ${BLUE}make help${NC}             - Show all available commands"
echo ""
echo -e "${YELLOW}Access URLs after starting:${NC}"
echo -e "  Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "  Backend:   ${GREEN}http://localhost:8000${NC}"
echo ""