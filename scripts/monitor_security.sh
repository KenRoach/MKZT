#!/bin/bash
set -e

# Configuration
LOG_FILE="/var/log/container_security.log"
ALERT_THRESHOLD=90  # CPU/Memory threshold for alerts
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL:-""}

# Function to send Slack notification
send_slack_alert() {
    local message="$1"
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -s -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 Security Alert: $message\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ALERT: $message" >> "$LOG_FILE"
}

# Function to check container resource usage
check_container_resources() {
    local container="$1"
    local cpu_usage
    local memory_usage
    
    cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" "$container" | sed 's/%//')
    memory_usage=$(docker stats --no-stream --format "{{.MemPerc}}" "$container" | sed 's/%//')
    
    if (( $(echo "$cpu_usage > $ALERT_THRESHOLD" | bc -l) )); then
        send_slack_alert "High CPU usage ($cpu_usage%) in container $container"
    fi
    
    if (( $(echo "$memory_usage > $ALERT_THRESHOLD" | bc -l) )); then
        send_slack_alert "High memory usage ($memory_usage%) in container $container"
    fi
}

# Function to check container security
check_container_security() {
    local container="$1"
    
    # Check if container is running as root
    if [ "$(docker exec "$container" whoami 2>/dev/null)" = "root" ]; then
        send_slack_alert "Container $container is running as root"
    fi
    
    # Check for exposed ports
    local exposed_ports
    exposed_ports=$(docker port "$container" 2>/dev/null)
    if [ -n "$exposed_ports" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO: Container $container has exposed ports: $exposed_ports" >> "$LOG_FILE"
    fi
    
    # Check container privileges
    if docker inspect --format='{{.HostConfig.Privileged}}' "$container" | grep -q "true"; then
        send_slack_alert "Container $container is running in privileged mode"
    fi
}

# Main monitoring loop
echo "Starting security monitoring..."
mkdir -p "$(dirname "$LOG_FILE")"

while true; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Running security checks..." >> "$LOG_FILE"
    
    # Get all running containers
    containers=$(docker ps --format "{{.Names}}")
    
    for container in $containers; do
        echo "Checking container: $container"
        check_container_resources "$container"
        check_container_security "$container"
    done
    
    # Check for container restarts
    docker events --filter 'type=container' --filter 'event=restart' --format '{{.Actor.Attributes.name}}' | \
    while read -r container; do
        send_slack_alert "Container $container has been restarted"
    done &
    
    # Check for failed health checks
    docker events --filter 'type=container' --filter 'event=health_status' --format '{{.Actor.Attributes.name}}:{{.Actor.Attributes.health_status}}' | \
    while read -r event; do
        container=$(echo "$event" | cut -d':' -f1)
        status=$(echo "$event" | cut -d':' -f2)
        if [ "$status" != "healthy" ]; then
            send_slack_alert "Container $container health check failed: $status"
        fi
    done &
    
    sleep 300  # Check every 5 minutes
done 