#!/bin/bash
# SOC Metrics Analyzer - Cron Uninstall Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Removing SOC Metrics Analyzer cron jobs...${NC}"

# Remove cron jobs
if crontab -l 2>/dev/null | grep -q "soc_metrics"; then
    crontab -l 2>/dev/null | grep -v "soc_metrics" | crontab -
    echo -e "${GREEN}✓ Cron jobs removed successfully!${NC}"
else
    echo -e "${YELLOW}No SOC Metrics cron jobs found${NC}"
fi
