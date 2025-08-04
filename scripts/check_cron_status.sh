#!/bin/bash
# SOC Metrics Analyzer - Cron Status Check Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/results/logs/cron.log"

echo -e "${BLUE}SOC Metrics Analyzer - Cron Status Check${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if cron jobs are installed
echo -e "${BLUE}Checking cron jobs...${NC}"
if crontab -l 2>/dev/null | grep -q "soc_metrics"; then
    echo -e "${GREEN}✓ Cron jobs are installed:${NC}"
    crontab -l | grep -E "(soc_metrics|SOC Metrics)" | while read -r line; do
        echo "  $line"
    done
else
    echo -e "${RED}✗ No SOC Metrics cron jobs found${NC}"
fi

# Check log files
echo -e "${BLUE}Checking log files...${NC}"
if [[ -f "$LOG_FILE" ]]; then
    echo -e "${GREEN}✓ Log file exists: $LOG_FILE${NC}"
    echo -e "${BLUE}Last 10 log entries:${NC}"
    tail -10 "$LOG_FILE" 2>/dev/null || echo "No log entries found"
else
    echo -e "${YELLOW}⚠ Log file not found: $LOG_FILE${NC}"
fi

# Check recent reports
echo -e "${BLUE}Checking recent reports...${NC}"
REPORTS_DIR="$PROJECT_DIR/results/reports"
if [[ -d "$REPORTS_DIR" ]]; then
    RECENT_REPORTS=$(find "$REPORTS_DIR" -name "*.xlsx" -mtime -7 2>/dev/null | wc -l)
    echo -e "${GREEN}✓ Reports directory exists${NC}"
    echo -e "${BLUE}Reports generated in last 7 days: $RECENT_REPORTS${NC}"
else
    echo -e "${YELLOW}⚠ Reports directory not found: $REPORTS_DIR${NC}"
fi

# Check Python environment
echo -e "${BLUE}Checking Python environment...${NC}"
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python3 is available: $(which python3)${NC}"
    python3 --version
else
    echo -e "${RED}✗ Python3 is not available${NC}"
fi

# Check .env file
echo -e "${BLUE}Checking configuration...${NC}"
if [[ -f "$PROJECT_DIR/.env" ]]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
else
    echo -e "${RED}✗ .env file not found${NC}"
fi
