# SOC Metrics Analyzer

A comprehensive Python tool for analyzing Security Operations Center (SOC) metrics from Jira tickets. Calculates Mean Time to Resolution (MTTR), Mean Time to Detection (MTD), and generates professional reports for SOC management.

## Features

- **MTTR/MTD Analysis**: Calculate key SOC performance metrics
- **Dual Analysis Types**: All tickets vs Production tickets (excluding testing/duplicates)
- **Flexible Time Periods**: All time, week, month, quarter, year, or custom periods
- **Professional Reports**: Excel spreadsheets, HTML reports, and visualizations
- **Automated Scheduling**: Cron job setup for regular reporting
- **Enterprise Ready**: SOC 2 Type II, GDPR, ISO 27001 compliance features
- **Security Focused**: Read-only Jira access, environment-based configuration

## Quick Start

### Prerequisites

- Python 3.8+
- Jira API access
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/1B05H1N/soc-metrics-analyzer.git
   cd soc-metrics-analyzer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env_example.txt .env
   # Edit .env with your Jira configuration
   ```

### Configuration

Create a `.env` file with your Jira credentials:

```bash
# Required: Jira Configuration
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@domain.com
JIRA_API_TOKEN=your-api-token
PROJECT_KEY=YOUR_PROJECT_KEY

# Required: Analysis Configuration
ANALYSIS_TYPE=ALL_TICKETS
TIME_PERIOD=LAST_WEEK
MAX_ISSUES=10000

# Optional: Organization Information (used in reports)
ORG_NAME=Your Organization
CONTACT_EMAIL=soc@yourorganization.com

# Optional: Email Notifications (disabled by default)
ENABLE_EMAIL_NOTIFICATIONS=false
```

### Usage

#### Basic Analysis

```bash
# Run analysis for all tickets
python main_direct.py --analysis-type ALL_TICKETS --time-period LAST_WEEK

# Run analysis excluding testing/duplicates
python main_direct.py --analysis-type EXCLUDE_TESTING_DUPLICATES --time-period LAST_MONTH

# Run both analysis types
python main_direct.py --analysis-type BOTH --time-period ALL_TIME
```

#### Time Periods

- `ALL_TIME`: Complete historical analysis
- `LAST_WEEK`: Last 7 days
- `LAST_MONTH`: Last 30 days
- `LAST_QUARTER`: Last 90 days
- `LAST_YEAR`: Last 365 days
- `CUSTOM`: Custom period (configured in .env)

#### Automated Scheduling

```bash
# Setup cron jobs for automated reporting
./scripts/setup_cron_jobs.sh

# Install cron jobs
./scripts/install_cron.sh

# Check cron status
./scripts/check_cron_status.sh
```

## Automated Scheduling & Scripts

The SOC Metrics Analyzer includes a comprehensive set of scripts for automated scheduling and maintenance. These scripts enable hands-off operation for regular reporting and system maintenance.

### Available Scripts

#### 1. `setup_cron_jobs.sh` - Initial Setup
**Purpose**: Creates the cron job configuration and necessary directories.

**What it does**:
- Creates cron job configuration file (`soc_metrics_cron.txt`)
- Sets up necessary directories for logs and reports
- Creates wrapper script for better error handling
- Configures automated cleanup jobs

**Usage**:
```bash
./scripts/setup_cron_jobs.sh
```

**Generated Cron Jobs**:
- **Weekly Report**: Every Monday at 9:00 AM (LAST_WEEK analysis)
- **Monthly Report**: First day of month at 9:00 AM (LAST_MONTH analysis)
- **Quarterly Report**: First day of quarter at 9:00 AM (LAST_QUARTER analysis)
- **Yearly Report**: January 1st at 9:00 AM (LAST_YEAR analysis)
- **Daily Health Check**: Every day at 6:00 AM (quick validation)
- **Log Rotation**: Every Sunday at 2:00 AM (removes logs older than 30 days)
- **Report Cleanup**: Every Sunday at 3:00 AM (removes reports older than 90 days)

#### 2. `install_cron.sh` - Install Cron Jobs
**Purpose**: Installs the configured cron jobs into the system.

**What it does**:
- Checks for existing SOC Metrics cron jobs
- Removes old entries if found
- Installs new cron jobs from configuration
- Provides status feedback

**Usage**:
```bash
./scripts/install_cron.sh
```

**Prerequisites**:
- Must run `setup_cron_jobs.sh` first
- Requires crontab access

#### 3. `check_cron_status.sh` - Status Monitoring
**Purpose**: Comprehensive status check of the automated system.

**What it checks**:
- Cron job installation status
- Recent log entries
- Report generation status
- Python environment
- Configuration file existence

**Usage**:
```bash
./scripts/check_cron_status.sh
```

**Output includes**:
- List of installed cron jobs
- Recent log entries
- Number of reports generated in last 7 days
- Python version and availability
- Configuration file status

#### 4. `uninstall_cron.sh` - Remove Cron Jobs
**Purpose**: Safely removes all SOC Metrics cron jobs.

**What it does**:
- Identifies SOC Metrics cron jobs
- Removes them from crontab
- Provides confirmation

**Usage**:
```bash
./scripts/uninstall_cron.sh
```

#### 5. `run_soc_metrics.sh` - Wrapper Script
**Purpose**: Provides robust error handling and logging for cron jobs.

**Features**:
- Prevents multiple simultaneous runs
- Comprehensive error logging
- Lock file management
- Environment validation

**Usage**:
```bash
./scripts/run_soc_metrics.sh [analysis_arguments]
```

### Complete Setup Process

#### Step 1: Initial Setup
```bash
# Navigate to project directory
cd soc-metrics-analyzer

# Make scripts executable
chmod +x scripts/*.sh

# Setup cron jobs configuration
./scripts/setup_cron_jobs.sh
```

#### Step 2: Configure Environment
```bash
# Copy environment template
cp env_example.txt .env

# Edit configuration
nano .env
```

**Required Configuration**:
```bash
# Jira Configuration
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@domain.com
JIRA_API_TOKEN=your-api-token
PROJECT_KEY=YOUR_PROJECT_KEY

# Analysis Configuration
ANALYSIS_TYPE=BOTH
TIME_PERIOD=LAST_WEEK
MAX_ISSUES=10000
```

#### Step 3: Install Cron Jobs
```bash
# Install automated cron jobs
./scripts/install_cron.sh
```

#### Step 4: Verify Installation
```bash
# Check system status
./scripts/check_cron_status.sh
```

### Maintenance & Monitoring

#### Daily Monitoring
```bash
# Check recent logs
tail -f results/logs/cron.log

# Check for errors
tail -f results/logs/cron_error.log

# View recent reports
ls -la results/reports/
```

#### Weekly Maintenance
```bash
# Check system status
./scripts/check_cron_status.sh

# Review log files
find results/logs/ -name "*.log" -mtime -7 -exec ls -la {} \;

# Check report generation
find results/reports/ -name "*.xlsx" -mtime -7 | wc -l
```

#### Monthly Maintenance
```bash
# Review cron job performance
grep "ERROR" results/logs/cron.log | tail -20

# Check disk usage
du -sh results/

# Verify configuration
cat .env | grep -E "(JIRA_|PROJECT_)"
```

### Troubleshooting Automated Jobs

#### Common Issues

**1. Cron Jobs Not Running**
```bash
# Check cron service status
sudo systemctl status cron

# Verify cron jobs are installed
crontab -l | grep soc_metrics

# Check cron logs
sudo tail -f /var/log/cron
```

**2. Permission Issues**
```bash
# Ensure scripts are executable
chmod +x scripts/*.sh

# Check file ownership
ls -la scripts/

# Verify Python path in cron
which python3
```

**3. Environment Issues**
```bash
# Test manual run
./scripts/run_soc_metrics.sh --time-period LAST_WEEK --max-issues 10

# Check Python environment
python3 --version
pip list | grep -E "(jira|pandas|matplotlib)"

# Verify .env file
cat .env
```

**4. Log Analysis**
```bash
# Check recent errors
grep "ERROR" results/logs/cron.log | tail -10

# Check successful runs
grep "completed successfully" results/logs/cron.log | tail -5

# Monitor real-time
tail -f results/logs/cron.log
```

### Customization

#### Modify Schedule
Edit `scripts/soc_metrics_cron.txt` to change timing:
```bash
# Example: Run weekly report on Fridays at 5 PM
0 17 * * 5 cd /path/to/project && python3 main_direct.py --time-period LAST_WEEK --analysis-type BOTH

# Example: Run daily at midnight
0 0 * * * cd /path/to/project && python3 main_direct.py --time-period LAST_WEEK --analysis-type ALL_TICKETS
```

#### Add Custom Reports
```bash
# Add to cron configuration
echo "0 10 1 * * cd $PROJECT_DIR && python3 main_direct.py --time-period ALL_TIME --analysis-type BOTH" >> scripts/soc_metrics_cron.txt

# Reinstall cron jobs
./scripts/install_cron.sh
```

#### Email Notifications
Enable email notifications in `.env`:
```bash
ENABLE_EMAIL_NOTIFICATIONS=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@domain.com
EMAIL_PASSWORD=your-app-password
NOTIFICATION_RECIPIENTS=soc@yourcompany.com
```

### Security Considerations

#### File Permissions
```bash
# Secure sensitive files
chmod 600 .env
chmod 600 results/logs/*.log

# Restrict script access
chmod 755 scripts/*.sh
```

#### Log Rotation
```bash
# Manual log cleanup
find results/logs/ -name "*.log" -mtime +30 -delete

# Manual report cleanup
find results/reports/ -name "*.xlsx" -mtime +90 -delete
```

#### Monitoring
```bash
# Set up monitoring alerts
echo "*/5 * * * * ./scripts/check_cron_status.sh | grep -q 'ERROR' && echo 'SOC Metrics Error Detected'" | crontab -

# Monitor disk usage
echo "0 2 * * * df -h | grep -q '90%' && echo 'Disk space low'" | crontab -
```

### Best Practices

#### 1. Regular Monitoring
- Check logs weekly for errors
- Monitor disk usage monthly
- Review report quality quarterly
- Update configurations as needed

#### 2. Backup Strategy
```bash
# Backup configuration
cp .env .env.backup.$(date +%Y%m%d)

# Backup reports
tar -czf reports_backup_$(date +%Y%m%d).tar.gz results/reports/

# Backup logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz results/logs/
```

#### 3. Performance Optimization
- Adjust `MAX_ISSUES` based on your data volume
- Use `--no-reports` for health checks
- Monitor API rate limits
- Consider timezone settings

#### 4. Documentation
- Keep configuration changes documented
- Record any customizations
- Maintain runbook for troubleshooting
- Update team on schedule changes

## Output

The tool generates comprehensive reports in the `results/` directory:

- **Excel Reports**: Multi-sheet spreadsheets with charts and tables
- **HTML Reports**: Interactive web-based reports
- **Visualizations**: PNG charts and graphs with professional styling
- **Text Summaries**: Quick overview and detailed analysis
- **Raw Data**: Processed data for further analysis

## Chart Guide

For detailed explanations of all generated charts and visualizations, see the comprehensive **[Chart Guide](CHART_GUIDE.md)**.

The SOC Metrics Analyzer generates several types of professional visualizations:

- **MTTR vs MTD Comparison Chart** (`mttr_mtd_comparison.png`)
- **Resolution Breakdown Chart** (`resolution_breakdown.png`)
- **Time Distribution Charts** (`time_distributions.png`)
- **Weekly Trends Chart** (`weekly_trends.png`)
- **Percentile Charts** (`percentile_charts.png`)
- **Outlier Analysis Chart** (`outlier_analysis.png`)

Each chart includes detailed explanations below the visualization and is designed for easy understanding by security teams and executives.

### Performance Benchmarks

#### Excellent Performance
- **MTTR**: < 4 hours (working hours)
- **MTD**: < 1 hour (working hours)
- **False Positive Rate**: < 10%
- **SLA Compliance**: > 95%

#### Good Performance
- **MTTR**: 4-8 hours (working hours)
- **MTD**: 1-2 hours (working hours)
- **False Positive Rate**: 10-20%
- **SLA Compliance**: 90-95%

#### Needs Improvement
- **MTTR**: > 8 hours (working hours)
- **MTD**: > 2 hours (working hours)
- **False Positive Rate**: > 20%
- **SLA Compliance**: < 90%

### Chart Interpretation Tips

#### Reading the Charts
1. **Always check the explanation box** below each chart
2. **Compare metrics** across different time periods
3. **Look for trends** rather than single data points
4. **Consider context** when interpreting outliers

#### Common Patterns
1. **Improving trends**: Declining MTTR/MTD over time
2. **Seasonal patterns**: Regular volume fluctuations
3. **Tool issues**: High false positive rates or detection delays
4. **Process bottlenecks**: Wide time distributions or high outliers

#### Red Flags
1. **Increasing MTTR**: May indicate resource constraints or process issues
2. **High false positive rates**: May indicate tool tuning needed
3. **Frequent outliers**: May indicate inconsistent processes
4. **Declining volume**: May indicate missed threats or tool failures

## Project Structure

```
soc-metrics-analyzer/
├── main_direct.py              # Main entry point
├── config.py                   # Configuration management
├── jira_client_direct.py      # Jira API integration
├── metrics_calculator.py      # Metrics calculation engine
├── excel_report_generator.py  # Excel report generation
├── report_generator.py        # HTML report generation
├── visualization_generator.py # Chart and graph generation
├── performance_monitor.py     # Performance monitoring
├── scheduler.py               # Automated scheduling
├── scripts/                   # Shell scripts for automation
│   ├── setup_cron_jobs.sh
│   ├── install_cron.sh
│   ├── uninstall_cron.sh
│   ├── check_cron_status.sh
│   └── run_soc_metrics.sh
├── requirements.txt           # Python dependencies
├── env_example.txt           # Environment template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Security Features

- **Read-only Access**: Only reads from Jira, never writes back
- **Environment Variables**: All sensitive data in .env files
- **Input Validation**: Comprehensive input sanitization
- **Error Handling**: Secure error messages without information disclosure
- **Audit Logging**: Comprehensive activity logging for compliance

## Enterprise Features

- **SOC 2 Type II Ready**: Designed with compliance requirements
- **GDPR Compliant**: Data privacy and retention controls
- **ISO 27001 Aligned**: Information security management standards
- **Zero Trust Principles**: Security-first design approach
- **Performance Monitoring**: Built-in performance tracking
- **Scalable Architecture**: Handles large datasets efficiently

## Metrics Calculated

### Core Metrics
- **MTTR**: Mean Time to Resolution
- **MTD**: Mean Time to Detection
- **Total Time**: Complete ticket lifecycle time
- **Working Hours**: Business hours calculations

### Advanced Metrics
- **SLA Compliance**: Breach detection and reporting
- **Performance Trends**: Weekly/monthly/quarterly trends
- **Resolution Breakdown**: Categorization analysis
- **Outlier Detection**: Statistical anomaly identification
- **Percentile Analysis**: 25th, 50th, 75th, 90th percentiles

### SOC-Specific Metrics
- **Priority Analysis**: High/Medium/Low priority breakdown
- **Severity Mapping**: Critical/High/Medium/Low severity
- **Alert Categories**: Security alert classification
- **Escalation Tracking**: Escalation frequency and patterns

## Configuration Options

### Analysis Types
- `ALL_TICKETS`: Include all tickets in analysis
- `EXCLUDE_TESTING_DUPLICATES`: Exclude testing and duplicate tickets
- `BOTH`: Run both analysis types

### Time Periods
- `ALL_TIME`: No time limit, all available data
- `LAST_WEEK`: Last 7 days
- `LAST_MONTH`: Last 30 days
- `LAST_QUARTER`: Last 90 days
- `LAST_YEAR`: Last 365 days
- `CUSTOM`: Custom period (configurable)

### SLA Thresholds
- Configurable SLA thresholds for different priority levels
- Breach detection and reporting
- Performance threshold monitoring

### Optional Features

#### Organization Information
The tool can include organization details in reports. These are completely optional:

```bash
# Optional: Organization Information (used in reports)
ORG_NAME=Your Organization
ORG_DEPARTMENT=Security Operations Center
CONTACT_EMAIL=soc@yourorganization.com
CONTACT_PHONE=+1-555-123-4567
ORG_WEBSITE=https://yourorganization.com
ORG_ADDRESS=123 Security Street, City, State 12345
SOC_MANAGER=SOC Manager
SOC_MANAGER_EMAIL=soc.manager@yourorganization.com
ESCALATION_CONTACT=Security Director
ESCALATION_EMAIL=security.director@yourorganization.com
```

#### Email Notifications
Email notifications are disabled by default. To enable:

```bash
# Optional: Email Notifications (disabled by default)
ENABLE_EMAIL_NOTIFICATIONS=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@domain.com
EMAIL_PASSWORD=your-app-password
NOTIFICATION_RECIPIENTS=soc@yourcompany.com
```

**Note**: Only configure email notifications if you specifically need them. The tool works perfectly without any notification settings.

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify Jira credentials in .env file
   - Ensure API token has read access to the project
   - Check Jira server URL format

2. **No Data Retrieved**
   - Verify project key is correct
   - Check ticket lifecycle configuration
   - Ensure tickets exist in the specified time period

3. **Memory Issues**
   - Reduce MAX_ISSUES in configuration
   - Enable memory optimization for large datasets
   - Monitor system resources during analysis

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main_direct.py --analysis-type ALL_TICKETS
```

## Performance Optimization

- **API Caching**: Reduces redundant API calls
- **Rate Limiting**: Prevents API abuse
- **Memory Optimization**: Efficient handling of large datasets
- **Parallel Processing**: Multi-threaded operations where applicable
- **Data Validation**: Early detection of data quality issues

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the configuration examples
3. Enable debug logging for detailed error information
4. Verify your Jira API access and permissions

## Disclaimer

**USE AT YOUR OWN RISK**

This software is provided "as is" without warranty of any kind, either express or implied. The author assumes no responsibility or liability for any damages, losses, or issues that may arise from the use of this software.

### Important Warnings

- **Data Access**: This tool accesses your Jira instance and retrieves ticket data. Ensure you have proper authorization and comply with your organization's data handling policies.
- **API Usage**: The tool makes API calls to your Jira instance. Monitor your API usage limits and ensure compliance with Jira's terms of service.
- **Data Processing**: This tool processes and analyzes security incident data. Handle all generated reports and data according to your organization's security policies.
- **No Warranty**: The author makes no representations or warranties about the accuracy, reliability, or suitability of this software for any purpose.
- **Limitation of Liability**: In no event shall the author be liable for any direct, indirect, incidental, special, exemplary, or consequential damages arising from the use of this software.

### User Responsibility

By using this software, you acknowledge that:
- You understand what this script does and how it works
- You have proper authorization to access the Jira data
- You will handle all generated data securely
- You will comply with your organization's security policies
- You use this software at your own risk

### Security Considerations

- Review all configuration settings before use
- Test in a non-production environment first
- Monitor API usage and rate limits
- Secure all generated reports and data
- Follow your organization's data retention policies

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This tool is designed for SOC teams to analyze their incident response metrics. Ensure you have proper authorization to access the Jira data and comply with your organization's data handling policies.
