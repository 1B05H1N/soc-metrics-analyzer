#!/bin/bash
# SOC Metrics Analyzer - Cron Installation Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_FILE="$SCRIPT_DIR/soc_metrics_cron.txt"

echo -e "${BLUE}Installing SOC Metrics Analyzer cron jobs...${NC}"

# Check if crontab is available
if ! command -v crontab &> /dev/null; then
    echo -e "${RED}Error: crontab is not available${NC}"
    exit 1
fi

# Check if cron file exists
if [[ ! -f "$CRON_FILE" ]]; then
    echo -e "${RED}Error: Cron configuration file not found. Run setup_cron_jobs.sh first.${NC}"
    exit 1
fi

# Install the cron jobs
if crontab -l 2>/dev/null | grep -q "soc_metrics"; then
    echo -e "${YELLOW}Warning: SOC Metrics cron jobs already exist. Removing old entries...${NC}"
    crontab -l 2>/dev/null | grep -v "soc_metrics" | crontab -
fi

# Add new cron jobs
crontab "$CRON_FILE"

echo -e "${GREEN}✓ Cron jobs installed successfully!${NC}"
echo -e "${BLUE}Current cron jobs:${NC}"
crontab -l | grep -E "(soc_metrics|SOC Metrics)"

echo -e "${BLUE}To view logs: tail -f results/logs/cron.log${NC}"
echo -e "${BLUE}To remove cron jobs: crontab -e${NC}"
