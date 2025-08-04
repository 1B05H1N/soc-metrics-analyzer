#!/usr/bin/env python3
"""
Configuration for SOC Metrics Tool
Centralized configuration for Jira connection, project settings, and analysis parameters
"""

import os
from typing import Dict, List, Any

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

class Config:
    """Configuration class for SOC Metrics Tool"""
    
    # Jira Connection Settings
    JIRA_SERVER = os.getenv('JIRA_SERVER', 'https://your-domain.atlassian.net')
    JIRA_USERNAME = os.getenv('JIRA_USERNAME', 'your-email@domain.com')
    JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN', 'your-api-token')
    PROJECT_KEY = os.getenv('PROJECT_KEY', 'YOUR_PROJECT_KEY')
    
    # Analysis Configuration
    MAX_ISSUES = int(os.getenv('MAX_ISSUES', '1000'))
    ANALYSIS_PERIOD_DAYS = int(os.getenv('ANALYSIS_PERIOD_DAYS', '30'))
    
    # SLA Configuration - Customize these thresholds for your organization
    SLA_THRESHOLDS = {
        'Critical': int(os.getenv('SLA_CRITICAL_HOURS', '4')),      # 4 hours for critical incidents
        'High': int(os.getenv('SLA_HIGH_HOURS', '8')),              # 8 hours for high priority
        'Medium': int(os.getenv('SLA_MEDIUM_HOURS', '24')),         # 24 hours for medium priority
        'Low': int(os.getenv('SLA_LOW_HOURS', '48')),               # 48 hours for low priority
        'Info': int(os.getenv('SLA_INFO_HOURS', '72'))              # 72 hours for informational
    }
    
    # Performance Thresholds - Define what constitutes excellent, good, acceptable, poor performance
    PERFORMANCE_THRESHOLDS = {
        'MTTR': {
            'excellent': float(os.getenv('MTTR_EXCELLENT_HOURS', '2.0')),      # < 2 hours
            'good': float(os.getenv('MTTR_GOOD_HOURS', '4.0')),               # < 4 hours
            'acceptable': float(os.getenv('MTTR_ACCEPTABLE_HOURS', '8.0')),    # < 8 hours
            'poor': float(os.getenv('MTTR_POOR_HOURS', '12.0'))               # > 12 hours
        },
        'MTD': {
            'excellent': float(os.getenv('MTD_EXCELLENT_HOURS', '0.5')),      # < 30 minutes
            'good': float(os.getenv('MTD_GOOD_HOURS', '1.0')),               # < 1 hour
            'acceptable': float(os.getenv('MTD_ACCEPTABLE_HOURS', '2.0')),    # < 2 hours
            'poor': float(os.getenv('MTD_POOR_HOURS', '4.0'))                # > 4 hours
        }
    }
    
    # Business Hours Configuration
    BUSINESS_HOURS = {
        'WORKING_HOURS_PER_DAY': int(os.getenv('WORKING_HOURS_PER_DAY', '8')),
        'WORKING_DAYS_PER_WEEK': int(os.getenv('WORKING_DAYS_PER_WEEK', '5')),
        'BUSINESS_HOURS_START': int(os.getenv('BUSINESS_HOURS_START', '9')),   # 9 AM
        'BUSINESS_HOURS_END': int(os.getenv('BUSINESS_HOURS_END', '17')),      # 5 PM
        'TIMEZONE': os.getenv('TIMEZONE', 'UTC')
    }
    
    # Scheduling Configuration
    SCHEDULING = {
        'WEEKLY': {
            'name': 'Weekly Metrics',
            'description': 'Weekly SOC performance metrics',
            'days_back': int(os.getenv('WEEKLY_DAYS_BACK', '7')),
            'report_prefix': os.getenv('WEEKLY_REPORT_PREFIX', 'weekly_soc_metrics'),
            'schedule': os.getenv('WEEKLY_CRON_SCHEDULE', '0 9 * * 1'),  # Every Monday at 9 AM
            'enabled': os.getenv('WEEKLY_ENABLED', 'true').lower() == 'true'
        },
        'MONTHLY': {
            'name': 'Monthly Metrics',
            'description': 'Monthly SOC performance metrics',
            'days_back': int(os.getenv('MONTHLY_DAYS_BACK', '30')),
            'report_prefix': os.getenv('MONTHLY_REPORT_PREFIX', 'monthly_soc_metrics'),
            'schedule': os.getenv('MONTHLY_CRON_SCHEDULE', '0 9 1 * *'),  # First day of month at 9 AM
            'enabled': os.getenv('MONTHLY_ENABLED', 'true').lower() == 'true'
        },
        'QUARTERLY': {
            'name': 'Quarterly Metrics',
            'description': 'Quarterly SOC performance metrics',
            'days_back': int(os.getenv('QUARTERLY_DAYS_BACK', '90')),
            'report_prefix': os.getenv('QUARTERLY_REPORT_PREFIX', 'quarterly_soc_metrics'),
            'schedule': os.getenv('QUARTERLY_CRON_SCHEDULE', '0 9 1 */3 *'),  # First day of quarter at 9 AM
            'enabled': os.getenv('QUARTERLY_ENABLED', 'true').lower() == 'true'
        },
        'YEARLY': {
            'name': 'Yearly Metrics',
            'description': 'Yearly SOC performance metrics',
            'days_back': int(os.getenv('YEARLY_DAYS_BACK', '365')),
            'report_prefix': os.getenv('YEARLY_REPORT_PREFIX', 'yearly_soc_metrics'),
            'schedule': os.getenv('YEARLY_CRON_SCHEDULE', '0 9 1 1 *'),  # January 1st at 9 AM
            'enabled': os.getenv('YEARLY_ENABLED', 'true').lower() == 'true'
        }
    }
    
    # Ticket Lifecycle Configuration - Customize for your specific workflow
    TICKET_LIFECYCLE = {
        # Status that indicates first action (detection time)
        'FIRST_ACTION_STATUS': os.getenv('FIRST_ACTION_STATUS', 'In Progress'),
        
        # Statuses that indicate completion (resolution time)
        'COMPLETION_STATUSES': (
            # Try to get from individual variables first
            [status for status in [
                os.getenv('COMPLETION_STATUS_1', ''),
                os.getenv('COMPLETION_STATUS_2', ''),
                os.getenv('COMPLETION_STATUS_3', ''),
                os.getenv('COMPLETION_STATUS_4', ''),
                os.getenv('COMPLETION_STATUS_5', '')
            ] if status] or
            # Fall back to comma-separated variable
            os.getenv('COMPLETION_STATUSES', 'Expected Activity,False Positive,True Positive,Duplicate,Testing').split(',')
        ),
        
        # Statuses to exclude from analysis (optional)
        'EXCLUDE_STATUSES': os.getenv('EXCLUDE_STATUSES', '').split(',') if os.getenv('EXCLUDE_STATUSES') else [],
        
        # Resolution mapping for categorization
        'RESOLUTION_MAPPING': {
            os.getenv('RESOLUTION_1_NAME', 'Expected Activity'): 'expected-activity',
            os.getenv('RESOLUTION_2_NAME', 'False Positive'): 'false-positive',
            os.getenv('RESOLUTION_3_NAME', 'True Positive'): 'true-positive', 
            os.getenv('RESOLUTION_4_NAME', 'Duplicate'): 'duplicate',
            os.getenv('RESOLUTION_5_NAME', 'Testing'): 'testing'
        }
    }
    
    # Analysis Types Configuration
    ANALYSIS_TYPES = {
        # Include all tickets (including testing and duplicates)
        'ALL_TICKETS': {
            'name': os.getenv('ALL_TICKETS_NAME', 'All Tickets Analysis'),
            'description': os.getenv('ALL_TICKETS_DESCRIPTION', 'Includes all tickets: expected-activity, false-positive, true-positive, duplicate, testing'),
            'exclude_statuses': []
        },
        
        # Exclude testing and duplicate tickets
        'EXCLUDE_TESTING_DUPLICATES': {
            'name': os.getenv('PRODUCTION_TICKETS_NAME', 'Production Tickets Analysis'), 
            'description': os.getenv('PRODUCTION_TICKETS_DESCRIPTION', 'Excludes testing and duplicate tickets, focuses on actual security incidents'),
            'exclude_statuses': os.getenv('PRODUCTION_EXCLUDE_STATUSES', 'Testing,Duplicate').split(',')
        }
    }
    
    # Time Calculation Settings
    WORKING_HOURS_PER_DAY = BUSINESS_HOURS['WORKING_HOURS_PER_DAY']
    WORKING_DAYS_PER_WEEK = BUSINESS_HOURS['WORKING_DAYS_PER_WEEK']
    WORKING_HOURS_PER_WEEK = WORKING_HOURS_PER_DAY * WORKING_DAYS_PER_WEEK
    
    # Report Output Settings
    REPORT_OUTPUT_DIR = os.getenv('REPORT_OUTPUT_DIR', 'results/reports')
    HTML_TEMPLATE_DIR = os.getenv('HTML_TEMPLATE_DIR', 'templates')
    EXCEL_TEMPLATE_PATH = os.getenv('EXCEL_TEMPLATE_PATH', 'templates/excel_template.xlsx')
    
    # Excel Report Configuration
    EXCEL_CONFIG = {
        'SHEETS': {
            'SUMMARY': os.getenv('EXCEL_SHEET_SUMMARY', 'Executive Summary'),
            'METRICS': os.getenv('EXCEL_SHEET_METRICS', 'Detailed Metrics'),
            'TRENDS': os.getenv('EXCEL_SHEET_TRENDS', 'Trends Analysis'),
            'BREAKDOWN': os.getenv('EXCEL_SHEET_BREAKDOWN', 'Resolution Breakdown'),
            'PERFORMANCE': os.getenv('EXCEL_SHEET_PERFORMANCE', 'Performance Analysis'),
            'SLA': os.getenv('EXCEL_SHEET_SLA', 'SLA Compliance'),
            'RAW_DATA': os.getenv('EXCEL_SHEET_RAW_DATA', 'Raw Data')
        },
        'CHARTS': {
            'MTTR_MTD_COMPARISON': os.getenv('EXCEL_CHART_MTTR_MTD', 'MTTR vs MTD Comparison'),
            'RESOLUTION_BREAKDOWN': os.getenv('EXCEL_CHART_RESOLUTION', 'Resolution Breakdown'),
            'TIME_DISTRIBUTION': os.getenv('EXCEL_CHART_TIME_DIST', 'Time Distribution'),
            'WEEKLY_TRENDS': os.getenv('EXCEL_CHART_WEEKLY', 'Weekly Trends'),
            'PERFORMANCE_SCORES': os.getenv('EXCEL_CHART_PERFORMANCE', 'Performance Scores'),
            'SLA_COMPLIANCE': os.getenv('EXCEL_CHART_SLA', 'SLA Compliance')
        },
        'TABLES': {
            'KEY_METRICS': os.getenv('EXCEL_TABLE_KEY_METRICS', 'Key Performance Metrics'),
            'RESOLUTION_SUMMARY': os.getenv('EXCEL_TABLE_RESOLUTION', 'Resolution Summary'),
            'PERFORMANCE_BREAKDOWN': os.getenv('EXCEL_TABLE_PERFORMANCE', 'Performance Breakdown'),
            'SLA_VIOLATIONS': os.getenv('EXCEL_TABLE_SLA', 'SLA Violations'),
            'TOP_ISSUES': os.getenv('EXCEL_TABLE_TOP_ISSUES', 'Top Issues by Time')
        }
    }
    
    # Date Range Settings
    DEFAULT_DAYS_BACK = int(os.getenv('DEFAULT_DAYS_BACK', '30'))
    MAX_DAYS_BACK = int(os.getenv('MAX_DAYS_BACK', '365'))
    
    # Time Period Configuration - Flexible reporting periods
    TIME_PERIODS = {
        'ALL_TIME': {
            'name': 'All Time',
            'description': 'Complete historical analysis of all available data',
            'days_back': 0,  # 0 means no limit - all available data
            'report_prefix': os.getenv('ALL_TIME_REPORT_PREFIX', 'all_time_soc_metrics'),
            'enabled': os.getenv('ALL_TIME_ENABLED', 'true').lower() == 'true'
        },
        'LAST_WEEK': {
            'name': 'Last Week',
            'description': 'Analysis of the last 7 days',
            'days_back': int(os.getenv('LAST_WEEK_DAYS_BACK', '7')),
            'report_prefix': os.getenv('LAST_WEEK_REPORT_PREFIX', 'last_week_soc_metrics'),
            'enabled': os.getenv('LAST_WEEK_ENABLED', 'true').lower() == 'true'
        },
        'LAST_MONTH': {
            'name': 'Last Month',
            'description': 'Analysis of the last 30 days',
            'days_back': int(os.getenv('LAST_MONTH_DAYS_BACK', '30')),
            'report_prefix': os.getenv('LAST_MONTH_REPORT_PREFIX', 'last_month_soc_metrics'),
            'enabled': os.getenv('LAST_MONTH_ENABLED', 'true').lower() == 'true'
        },
        'LAST_QUARTER': {
            'name': 'Last Quarter',
            'description': 'Analysis of the last 90 days',
            'days_back': int(os.getenv('LAST_QUARTER_DAYS_BACK', '90')),
            'report_prefix': os.getenv('LAST_QUARTER_REPORT_PREFIX', 'last_quarter_soc_metrics'),
            'enabled': os.getenv('LAST_QUARTER_ENABLED', 'true').lower() == 'true'
        },
        'LAST_YEAR': {
            'name': 'Last Year',
            'description': 'Analysis of the last 365 days',
            'days_back': int(os.getenv('LAST_YEAR_DAYS_BACK', '365')),
            'report_prefix': os.getenv('LAST_YEAR_REPORT_PREFIX', 'last_year_soc_metrics'),
            'enabled': os.getenv('LAST_YEAR_ENABLED', 'true').lower() == 'true'
        },
        'CUSTOM': {
            'name': 'Custom Period',
            'description': 'Custom time period specified in configuration',
            'days_back': int(os.getenv('CUSTOM_DAYS_BACK', '60')),
            'report_prefix': os.getenv('CUSTOM_REPORT_PREFIX', 'custom_soc_metrics'),
            'enabled': os.getenv('CUSTOM_ENABLED', 'true').lower() == 'true'
        }
    }
    
    # Alert Categories for SOC Analysis - Customize for your threat landscape
    ALERT_CATEGORIES = {
        'phishing': os.getenv('ALERT_CATEGORY_PHISHING', 'phishing,email,spam,suspicious_email').split(','),
        'malware': os.getenv('ALERT_CATEGORY_MALWARE', 'malware,virus,trojan,ransomware,malicious').split(','),
        'access_control': os.getenv('ALERT_CATEGORY_ACCESS', 'login,authentication,access,unauthorized').split(','),
        'network_security': os.getenv('ALERT_CATEGORY_NETWORK', 'network,traffic,firewall,ddos').split(','),
        'data_protection': os.getenv('ALERT_CATEGORY_DATA', 'data,leak,breach,pii,sensitive').split(','),
        'general': []  # Default category
    }
    
    # Priority to Severity Mapping - Customize based on your Jira priority levels
    PRIORITY_SEVERITY_MAPPING = {
        os.getenv('PRIORITY_HIGHEST', 'Highest'): 'Critical',
        os.getenv('PRIORITY_HIGH', 'High'): 'High', 
        os.getenv('PRIORITY_MEDIUM', 'Medium'): 'Medium',
        os.getenv('PRIORITY_LOW', 'Low'): 'Low',
        os.getenv('PRIORITY_LOWEST', 'Lowest'): 'Low'
    }
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE = os.getenv('LOG_FILE', 'results/logs/soc_metrics.log')
    
    # API Settings
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '1'))  # seconds between requests
    
    # Visualization Settings
    CHART_STYLE = os.getenv('CHART_STYLE', 'seaborn-v0_8')
    CHART_PALETTE = os.getenv('CHART_PALETTE', 'husl')
    CHART_DPI = int(os.getenv('CHART_DPI', '300'))
    CHART_FORMAT = os.getenv('CHART_FORMAT', 'png')
    
    # Notification Settings (Optional)
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    NOTIFICATION_RECIPIENTS = os.getenv('NOTIFICATION_RECIPIENTS', '').split(',')

    # Data Retention Settings
    LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', '30'))
    REPORT_RETENTION_DAYS = int(os.getenv('REPORT_RETENTION_DAYS', '90'))
    DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', '365'))

    # Organization Information (Optional - used in reports)
    ORGANIZATION_INFO = {
        'name': os.getenv('ORG_NAME', ''),
        'department': os.getenv('ORG_DEPARTMENT', ''),
        'contact_email': os.getenv('CONTACT_EMAIL', ''),
        'contact_phone': os.getenv('CONTACT_PHONE', ''),
        'website': os.getenv('ORG_WEBSITE', ''),
        'address': os.getenv('ORG_ADDRESS', ''),
        'timezone': os.getenv('ORG_TIMEZONE', 'UTC'),
        'soc_manager': os.getenv('SOC_MANAGER', ''),
        'soc_manager_email': os.getenv('SOC_MANAGER_EMAIL', ''),
        'escalation_contact': os.getenv('ESCALATION_CONTACT', ''),
        'escalation_email': os.getenv('ESCALATION_EMAIL', '')
    }
    
    # Report Customization
    REPORT_CUSTOMIZATION = {
        'company_logo_path': os.getenv('COMPANY_LOGO_PATH', ''),
        'report_footer': os.getenv('REPORT_FOOTER', 'Generated by SOC Metrics Analyzer'),
        'report_header': os.getenv('REPORT_HEADER', 'SOC Performance Metrics Report'),
        'include_contact_info': os.getenv('INCLUDE_CONTACT_INFO', 'true').lower() == 'true',
        'include_disclaimer': os.getenv('INCLUDE_DISCLAIMER', 'true').lower() == 'true',
        'disclaimer_text': os.getenv('DISCLAIMER_TEXT', 'This report contains sensitive security information. Handle with appropriate care.'),
        'report_template': os.getenv('REPORT_TEMPLATE', 'default')
    }
    
    # Debug Settings
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    VERBOSE_LOGGING = os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true'
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        required_env_vars = ['JIRA_SERVER', 'JIRA_USERNAME', 'JIRA_API_TOKEN', 'PROJECT_KEY']
        
        missing_vars = []
        for var in required_env_vars:
            if not getattr(cls, var) or getattr(cls, var).startswith('your-'):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
            print("Please update your .env file with the correct values.")
            return False
        
        # Validate SLA thresholds
        for severity, hours in cls.SLA_THRESHOLDS.items():
            if hours <= 0:
                print(f"ERROR: Invalid SLA threshold for {severity}: {hours} hours")
                return False
        
        # Validate performance thresholds
        for metric, thresholds in cls.PERFORMANCE_THRESHOLDS.items():
            for level, value in thresholds.items():
                if value < 0:
                    print(f"ERROR: Invalid performance threshold for {metric}.{level}: {value}")
                    return False
        
        # Validate business hours
        if cls.BUSINESS_HOURS['WORKING_HOURS_PER_DAY'] <= 0 or cls.BUSINESS_HOURS['WORKING_HOURS_PER_DAY'] > 24:
            print(f"ERROR: Invalid working hours per day: {cls.BUSINESS_HOURS['WORKING_HOURS_PER_DAY']}")
            return False
        
        if cls.BUSINESS_HOURS['WORKING_DAYS_PER_WEEK'] <= 0 or cls.BUSINESS_HOURS['WORKING_DAYS_PER_WEEK'] > 7:
            print(f"ERROR: Invalid working days per week: {cls.BUSINESS_HOURS['WORKING_DAYS_PER_WEEK']}")
            return False
        
        # Validate time periods
        for period, config in cls.TIME_PERIODS.items():
            if config['days_back'] < 0:
                print(f"ERROR: Invalid days_back for {period}: {config['days_back']}")
                return False
        
        # Validate analysis types
        for analysis_type, config in cls.ANALYSIS_TYPES.items():
            if not config.get('name') or not config.get('description'):
                print(f"ERROR: Invalid analysis type configuration for {analysis_type}")
                return False
        
        print("SUCCESS: Configuration validation passed")
        return True
    
    @classmethod
    def get_analysis_config(cls, analysis_type: str = 'ALL_TICKETS') -> Dict:
        """Get configuration for specific analysis type"""
        if analysis_type not in cls.ANALYSIS_TYPES:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        return cls.ANALYSIS_TYPES[analysis_type]
    
    @classmethod
    def get_excluded_statuses(cls, analysis_type: str = 'ALL_TICKETS') -> List[str]:
        """Get list of statuses to exclude for given analysis type"""
        config = cls.get_analysis_config(analysis_type)
        return config.get('exclude_statuses', [])
    
    @classmethod
    def get_completion_statuses(cls) -> List[str]:
        """Get list of statuses that indicate ticket completion"""
        return cls.TICKET_LIFECYCLE['COMPLETION_STATUSES']
    
    @classmethod
    def get_first_action_status(cls) -> str:
        """Get status that indicates first action (detection time)"""
        return cls.TICKET_LIFECYCLE['FIRST_ACTION_STATUS']
    
    @classmethod
    def get_resolution_mapping(cls) -> Dict[str, str]:
        """Get mapping of status names to resolution categories"""
        return cls.TICKET_LIFECYCLE['RESOLUTION_MAPPING']
    
    @classmethod
    def get_scheduling_config(cls, schedule_type: str) -> Dict:
        """Get configuration for specific scheduling type"""
        if schedule_type not in cls.SCHEDULING:
            raise ValueError(f"Unknown schedule type: {schedule_type}")
        
        return cls.SCHEDULING[schedule_type]
    
    @classmethod
    def get_all_scheduling_types(cls) -> List[str]:
        """Get list of all available scheduling types"""
        return list(cls.SCHEDULING.keys())
    
    @classmethod
    def get_sla_threshold(cls, severity: str) -> int:
        """Get SLA threshold for given severity level"""
        return cls.SLA_THRESHOLDS.get(severity, cls.SLA_THRESHOLDS['Medium'])
    
    @classmethod
    def get_performance_threshold(cls, metric: str, level: str) -> float:
        """Get performance threshold for given metric and level"""
        return cls.PERFORMANCE_THRESHOLDS.get(metric, {}).get(level, 0.0)
    
    @classmethod
    def get_time_period_config(cls, period: str) -> Dict:
        """Get configuration for specific time period"""
        if period not in cls.TIME_PERIODS:
            raise ValueError(f"Unknown time period: {period}")
        
        return cls.TIME_PERIODS[period]
    
    @classmethod
    def get_all_time_periods(cls) -> List[str]:
        """Get list of all available time periods"""
        return list(cls.TIME_PERIODS.keys())
    
    @classmethod
    def get_enabled_time_periods(cls) -> List[str]:
        """Get list of enabled time periods"""
        return [period for period in cls.TIME_PERIODS.keys() 
                if cls.TIME_PERIODS[period]['enabled']]
    
    @classmethod
    def get_organization_info(cls) -> Dict[str, str]:
        """Get organization information"""
        return cls.ORGANIZATION_INFO
    
    @classmethod
    def get_report_customization(cls) -> Dict[str, Any]:
        """Get report customization settings"""
        return cls.REPORT_CUSTOMIZATION
    
    @classmethod
    def get_contact_info(cls) -> Dict[str, str]:
        """Get contact information for reports"""
        return {
            'soc_manager': cls.ORGANIZATION_INFO['soc_manager'],
            'soc_manager_email': cls.ORGANIZATION_INFO['soc_manager_email'],
            'escalation_contact': cls.ORGANIZATION_INFO['escalation_contact'],
            'escalation_email': cls.ORGANIZATION_INFO['escalation_email'],
            'contact_email': cls.ORGANIZATION_INFO['contact_email'],
            'contact_phone': cls.ORGANIZATION_INFO['contact_phone']
        } 