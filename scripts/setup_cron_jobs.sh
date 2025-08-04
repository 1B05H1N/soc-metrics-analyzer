#!/bin/bash
# SOC Metrics Analyzer - Cron Job Setup Script
# This script sets up automated cron jobs for regular SOC metrics reporting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_PATH="$(which python3)"
LOG_FILE="$PROJECT_DIR/results/logs/cron.log"
CRON_FILE="$SCRIPT_DIR/soc_metrics_cron.txt"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}SOC Metrics Analyzer - Cron Job Setup${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if running as root (optional)
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}Warning: Running as root. This is not recommended for security reasons.${NC}"
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not installed or not in PATH${NC}"
    exit 1
fi

# Check if the main script exists
if [[ ! -f "$PROJECT_DIR/main_direct.py" ]]; then
    echo -e "${RED}Error: main_direct.py not found in $PROJECT_DIR${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${BLUE}Creating necessary directories...${NC}"
mkdir -p "$PROJECT_DIR/results/logs"
mkdir -p "$PROJECT_DIR/results/reports"

# Create the cron jobs file
echo -e "${BLUE}Creating cron jobs configuration...${NC}"

cat > "$CRON_FILE" << EOF
# SOC Metrics Analyzer - Automated Cron Jobs
# Generated on $(date)
# 
# These cron jobs will automatically run SOC metrics analysis at scheduled intervals
# 
# Cron job format: minute hour day month day_of_week command
# 
# Examples:
# 0 9 * * 1     = Every Monday at 9:00 AM
# 0 9 1 * *     = First day of month at 9:00 AM  
# 0 9 1 */3 *   = First day of quarter at 9:00 AM
# 0 9 1 1 *     = January 1st at 9:00 AM

# Weekly SOC Metrics Report (Every Monday at 9:00 AM)
0 9 * * 1 cd $PROJECT_DIR && $PYTHON_PATH main_direct.py --time-period LAST_WEEK --analysis-type BOTH --max-issues 10000 >> $LOG_FILE 2>&1

# Monthly SOC Metrics Report (First day of month at 9:00 AM)
0 9 1 * * cd $PROJECT_DIR && $PYTHON_PATH main_direct.py --time-period LAST_MONTH --analysis-type BOTH --max-issues 10000 >> $LOG_FILE 2>&1

# Quarterly SOC Metrics Report (First day of quarter at 9:00 AM)
0 9 1 */3 * cd $PROJECT_DIR && $PYTHON_PATH main_direct.py --time-period LAST_QUARTER --analysis-type BOTH --max-issues 10000 >> $LOG_FILE 2>&1

# Yearly SOC Metrics Report (January 1st at 9:00 AM)
0 9 1 1 * cd $PROJECT_DIR && $PYTHON_PATH main_direct.py --time-period LAST_YEAR --analysis-type BOTH --max-issues 10000 >> $LOG_FILE 2>&1

# Daily Health Check (Every day at 6:00 AM - runs with limited issues for quick check)
0 6 * * * cd $PROJECT_DIR && $PYTHON_PATH main_direct.py --time-period LAST_WEEK --analysis-type ALL_TICKETS --max-issues 100 --no-reports >> $LOG_FILE 2>&1

# Log Rotation (Every Sunday at 2:00 AM)
0 2 * * 0 find $PROJECT_DIR/results/logs -name "*.log" -mtime +30 -delete >> $LOG_FILE 2>&1

# Report Cleanup (Every Sunday at 3:00 AM - keep reports for 90 days)
0 3 * * 0 find $PROJECT_DIR/results/reports -name "*.xlsx" -mtime +90 -delete >> $LOG_FILE 2>&1
0 3 * * 0 find $PROJECT_DIR/results/reports -name "*.html" -mtime +90 -delete >> $LOG_FILE 2>&1
0 3 * * 0 find $PROJECT_DIR/results/reports -name "*.png" -mtime +90 -delete >> $LOG_FILE 2>&1
EOF

echo -e "${GREEN}✓ Cron jobs configuration created: $CRON_FILE${NC}"

# Create a wrapper script for better error handling
echo -e "${BLUE}Creating wrapper script for better error handling...${NC}"

cat > "$SCRIPT_DIR/run_soc_metrics.sh" << 'EOF'
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
EOF

chmod +x "$SCRIPT_DIR/run_soc_metrics.sh"
echo -e "${GREEN}✓ Wrapper script created: $SCRIPT_DIR/run_soc_metrics.sh${NC}"

# Create installation script
echo -e "${BLUE}Creating installation script...${NC}"

cat > "$SCRIPT_DIR/install_cron.sh" << 'EOF'
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
EOF

chmod +x "$SCRIPT_DIR/install_cron.sh"
echo -e "${GREEN}✓ Installation script created: $SCRIPT_DIR/install_cron.sh${NC}"

# Create uninstall script
echo -e "${BLUE}Creating uninstall script...${NC}"

cat > "$SCRIPT_DIR/uninstall_cron.sh" << 'EOF'
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
EOF

chmod +x "$SCRIPT_DIR/uninstall_cron.sh"
echo -e "${GREEN}✓ Uninstall script created: $SCRIPT_DIR/uninstall_cron.sh${NC}"

# Create status check script
echo -e "${BLUE}Creating status check script...${NC}"

cat > "$SCRIPT_DIR/check_cron_status.sh" << 'EOF'
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
EOF

chmod +x "$SCRIPT_DIR/check_cron_status.sh"
echo -e "${GREEN}✓ Status check script created: $SCRIPT_DIR/check_cron_status.sh${NC}"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. ${YELLOW}Copy env_example.txt to .env and configure your settings${NC}"
echo -e "2. ${YELLOW}Run: ./scripts/install_cron.sh${NC}"
echo -e "3. ${YELLOW}Check status: ./scripts/check_cron_status.sh${NC}"
echo -e "4. ${YELLOW}View logs: tail -f results/logs/cron.log${NC}"
echo -e "5. ${YELLOW}To remove cron jobs: ./scripts/uninstall_cron.sh${NC}"
echo -e "${BLUE}========================================${NC}" 