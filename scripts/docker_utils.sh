#!/bin/bash

# Function to display help message
show_help() {
    echo "WhatsApp AI Ordering Bot Docker Utilities"
    echo ""
    echo "Usage: ./docker_utils.sh [command]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker images"
    echo "  up          Start the containers"
    echo "  down        Stop the containers"
    echo "  logs        Show container logs"
    echo "  shell       Open a shell in the app container"
    echo "  test        Run tests in the app container"
    echo "  migrate     Run database migrations"
    echo "  help        Show this help message"
    echo ""
}

# Function to build Docker images
build() {
    echo "Building Docker images..."
    docker-compose build
}

# Function to start containers
up() {
    echo "Starting containers..."
    docker-compose up -d
}

# Function to stop containers
down() {
    echo "Stopping containers..."
    docker-compose down
}

# Function to show container logs
logs() {
    echo "Showing container logs..."
    docker-compose logs -f
}

# Function to open a shell in the app container
shell() {
    echo "Opening shell in app container..."
    docker-compose exec app /bin/bash
}

# Function to run tests
test() {
    echo "Running tests..."
    docker-compose exec app pytest
}

# Function to run migrations
migrate() {
    echo "Running database migrations..."
    docker-compose exec app python scripts/init_db.py
}

# Main script logic
case "$1" in
    build)
        build
        ;;
    up)
        up
        ;;
    down)
        down
        ;;
    logs)
        logs
        ;;
    shell)
        shell
        ;;
    test)
        test
        ;;
    migrate)
        migrate
        ;;
    help|*)
        show_help
        ;;
esac 