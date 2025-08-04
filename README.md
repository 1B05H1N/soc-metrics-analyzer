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

## Output

The tool generates comprehensive reports in the `results/` directory:

- **Excel Reports**: Multi-sheet spreadsheets with charts and tables
- **HTML Reports**: Interactive web-based reports
- **Visualizations**: PNG charts and graphs
- **Text Summaries**: Quick overview and detailed analysis
- **Raw Data**: Processed data for further analysis

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
EMAIL_PASSWORD=your-email-password
NOTIFICATION_RECIPIENTS=soc@domain.com
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
