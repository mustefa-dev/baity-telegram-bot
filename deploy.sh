#!/bin/bash

# Baity Telegram Bot - Deployment Script
# Usage: ./deploy.sh [command]
# Commands: start, stop, restart, logs, status, build, update

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_NAME="baity-bot"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_env() {
    if [ ! -f .env ]; then
        log_error ".env file not found!"
        log_info "Copy .env.example to .env and configure it:"
        log_info "  cp .env.example .env"
        exit 1
    fi
}

build() {
    log_info "Building Docker images..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME build --no-cache
    log_info "Build complete!"
}

start() {
    check_env
    log_info "Starting Baity Telegram Bot..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
    log_info "Bot started! Checking health..."
    sleep 5
    status
}

stop() {
    log_info "Stopping Baity Telegram Bot..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down
    log_info "Bot stopped!"
}

restart() {
    log_info "Restarting Baity Telegram Bot..."
    stop
    start
}

logs() {
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f --tail=100
}

status() {
    log_info "Container Status:"
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps

    echo ""
    log_info "Health Check:"

    if curl -s http://localhost:8000/api/v1/health/live > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Bot is healthy${NC}"
    else
        echo -e "${RED}✗ Bot is not responding${NC}"
    fi
}

update() {
    log_info "Updating Baity Telegram Bot..."

    # Pull latest code (if using git)
    if [ -d .git ]; then
        log_info "Pulling latest code..."
        git pull
    fi

    # Rebuild and restart
    build
    restart

    log_info "Update complete!"
}

# Start with nginx (for SSL)
start_with_nginx() {
    check_env
    log_info "Starting with Nginx reverse proxy..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME --profile with-nginx up -d
    log_info "Started with Nginx!"
}

# Show help
help() {
    echo "Baity Telegram Bot - Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       Start the bot"
    echo "  stop        Stop the bot"
    echo "  restart     Restart the bot"
    echo "  logs        View logs (follow mode)"
    echo "  status      Check bot status"
    echo "  build       Build Docker images"
    echo "  update      Pull code, rebuild, and restart"
    echo "  nginx       Start with Nginx (for SSL)"
    echo "  help        Show this help message"
}

# Main
case "${1:-help}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    build)
        build
        ;;
    update)
        update
        ;;
    nginx)
        start_with_nginx
        ;;
    help|*)
        help
        ;;
esac
