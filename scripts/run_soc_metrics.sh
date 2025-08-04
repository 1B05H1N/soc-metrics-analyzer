#!/bin/bash
# SOC Metrics Analyzer - Wrapper Script
# This script provides better error handling and logging for cron jobs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/results/logs/cron.log"
ERROR_LOG="$PROJECT_DIR/results/logs/cron_error.log"
LOCK_FILE="$PROJECT_DIR/soc_metrics.lock"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to log errors
log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$ERROR_LOG"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$LOG_FILE"
}

# Check if already running
if [[ -f "$LOCK_FILE" ]]; then
    PID=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    if ps -p "$PID" > /dev/null 2>&1; then
        log_error "SOC Metrics Analyzer is already running (PID: $PID)"
        exit 1
    else
        # Remove stale lock file
        rm -f "$LOCK_FILE"
    fi
fi

# Create lock file
echo $$ > "$LOCK_FILE"

# Trap to clean up lock file on exit
trap 'rm -f "$LOCK_FILE"' EXIT

# Log start
log_message "Starting SOC Metrics Analysis"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    log_error "Python3 is not available"
    exit 1
fi

# Check if .env file exists
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    log_error ".env file not found. Please copy env_example.txt to .env and configure it."
    exit 1
fi

# Run the analysis with the provided arguments
cd "$PROJECT_DIR"
if python3 main_direct.py "$@"; then
    log_message "SOC Metrics Analysis completed successfully"
else
    log_error "SOC Metrics Analysis failed"
    exit 1
fi
