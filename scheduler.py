#!/usr/bin/env python3
"""
SOC Metrics Scheduler
Automated scheduling for weekly, monthly, quarterly, and yearly reports
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import subprocess
import logging

from config import Config
from main_direct import SOCMetricsAnalyzer

class SOCMetricsScheduler:
    """Scheduler for automated SOC metrics reports"""
    
    def __init__(self):
        self.analyzer = SOCMetricsAnalyzer()
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        Path("logs").mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format=Config.LOG_FORMAT,
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_scheduled_report(self, schedule_type: str, analysis_type: str = 'ALL_TICKETS') -> bool:
        """Run a scheduled report"""
        try:
            # Get scheduling configuration
            schedule_config = Config.get_scheduling_config(schedule_type)
            
            self.logger.info(f"Starting {schedule_type} report generation")
            self.logger.info(f"Schedule: {schedule_config['name']}")
            self.logger.info(f"Days back: {schedule_config['days_back']}")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=schedule_config['days_back'])
            
            # Create report filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_prefix = schedule_config['report_prefix']
            
            # Run analysis
            success = self.analyzer.run_analysis(
                max_issues=Config.MAX_ISSUES,
                generate_reports=True,
                analysis_type=analysis_type,
                schedule_type=schedule_type,
                start_date=start_date,
                end_date=end_date,
                report_prefix=report_prefix
            )
            
            if success:
                self.logger.info(f"SUCCESS: {schedule_type} report generated successfully")
            else:
                self.logger.error(f"ERROR: {schedule_type} report generation failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"ERROR: Failed to generate {schedule_type} report: {e}")
            return False
    
    def run_weekly_report(self, analysis_type: str = 'ALL_TICKETS') -> bool:
        """Run weekly metrics report"""
        return self.run_scheduled_report('WEEKLY', analysis_type)
    
    def run_monthly_report(self, analysis_type: str = 'ALL_TICKETS') -> bool:
        """Run monthly metrics report"""
        return self.run_scheduled_report('MONTHLY', analysis_type)
    
    def run_quarterly_report(self, analysis_type: str = 'ALL_TICKETS') -> bool:
        """Run quarterly metrics report"""
        return self.run_scheduled_report('QUARTERLY', analysis_type)
    
    def run_yearly_report(self, analysis_type: str = 'ALL_TICKETS') -> bool:
        """Run yearly metrics report"""
        return self.run_scheduled_report('YEARLY', analysis_type)
    
    def run_all_reports(self, analysis_type: str = 'ALL_TICKETS') -> Dict[str, bool]:
        """Run all scheduled reports"""
        results = {}
        
        for schedule_type in Config.get_all_scheduling_types():
            schedule_config = Config.get_scheduling_config(schedule_type)
            if schedule_config.get('enabled', True):
                self.logger.info(f"Running {schedule_type} report...")
                results[schedule_type] = self.run_scheduled_report(schedule_type, analysis_type)
            else:
                self.logger.info(f"Skipping {schedule_type} report (disabled)")
                results[schedule_type] = False
        
        return results
    
    def create_cron_jobs(self) -> bool:
        """Create cron jobs for automated scheduling"""
        try:
            cron_content = []
            
            for schedule_type in Config.get_all_scheduling_types():
                schedule_config = Config.get_scheduling_config(schedule_type)
                if schedule_config.get('enabled', True):
                    # Get the current working directory
                    current_dir = os.getcwd()
                    python_path = sys.executable
                    
                    cron_line = f"{schedule_config['schedule']} cd {current_dir} && {python_path} scheduler.py --{schedule_type.lower()}"
                    cron_content.append(cron_line)
            
            # Write cron file
            cron_file = "soc_metrics_cron.txt"
            with open(cron_file, 'w') as f:
                f.write("# SOC Metrics Tool Cron Jobs\n")
                f.write("# Add these lines to your crontab:\n")
                f.write("# crontab -e\n")
                f.write("# Then add the lines below:\n\n")
                for line in cron_content:
                    f.write(f"{line}\n")
            
            self.logger.info(f"SUCCESS: Cron jobs written to {cron_file}")
            self.logger.info("To install cron jobs, run: crontab soc_metrics_cron.txt")
            
            return True
            
        except Exception as e:
            self.logger.error(f"ERROR: Failed to create cron jobs: {e}")
            return False
    
    def create_windows_task(self) -> bool:
        """Create Windows Task Scheduler tasks"""
        try:
            current_dir = os.getcwd()
            python_path = sys.executable
            
            # Create batch file for each schedule type
            for schedule_type in Config.get_all_scheduling_types():
                schedule_config = Config.get_scheduling_config(schedule_type)
                if schedule_config.get('enabled', True):
                    batch_file = f"run_{schedule_type.lower()}.bat"
                    
                    with open(batch_file, 'w') as f:
                        f.write(f"@echo off\n")
                        f.write(f"cd /d {current_dir}\n")
                        f.write(f"{python_path} scheduler.py --{schedule_type.lower()}\n")
                        f.write(f"pause\n")
                    
                    self.logger.info(f"Created batch file: {batch_file}")
            
            # Create PowerShell script for Windows Task Scheduler
            ps_script = "create_windows_tasks.ps1"
            with open(ps_script, 'w') as f:
                f.write("# PowerShell script to create Windows Task Scheduler tasks\n")
                f.write("# Run as Administrator\n\n")
                
                for schedule_type in Config.get_all_scheduling_types():
                    schedule_config = Config.get_scheduling_config(schedule_type)
                    if schedule_config.get('enabled', True):
                        task_name = f"SOC_Metrics_{schedule_type}"
                        batch_file = f"run_{schedule_type.lower()}.bat"
                        
                        f.write(f"# Create {schedule_type} task\n")
                        f.write(f'$action = New-ScheduledTaskAction -Execute "{batch_file}"\n')
                        f.write(f'$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9AM\n')
                        f.write(f'Register-ScheduledTask -TaskName "{task_name}" -Action $action -Trigger $trigger\n\n')
            
            self.logger.info(f"SUCCESS: Windows task files created")
            self.logger.info(f"Run {ps_script} as Administrator to create scheduled tasks")
            
            return True
            
        except Exception as e:
            self.logger.error(f"ERROR: Failed to create Windows tasks: {e}")
            return False

def main():
    """Main entry point for scheduler"""
    parser = argparse.ArgumentParser(description='SOC Metrics Scheduler')
    parser.add_argument('--weekly', action='store_true', help='Run weekly report')
    parser.add_argument('--monthly', action='store_true', help='Run monthly report')
    parser.add_argument('--quarterly', action='store_true', help='Run quarterly report')
    parser.add_argument('--yearly', action='store_true', help='Run yearly report')
    parser.add_argument('--all', action='store_true', help='Run all reports')
    parser.add_argument('--create-cron', action='store_true', help='Create cron jobs')
    parser.add_argument('--create-windows-tasks', action='store_true', help='Create Windows tasks')
    parser.add_argument('--analysis-type', choices=['ALL_TICKETS', 'EXCLUDE_TESTING_DUPLICATES', 'BOTH'],
                       default='ALL_TICKETS', help='Type of analysis to run')
    
    args = parser.parse_args()
    
    scheduler = SOCMetricsScheduler()
    
    if args.create_cron:
        success = scheduler.create_cron_jobs()
        sys.exit(0 if success else 1)
    
    if args.create_windows_tasks:
        success = scheduler.create_windows_task()
        sys.exit(0 if success else 1)
    
    if args.all:
        results = scheduler.run_all_reports(args.analysis_type)
        success = all(results.values())
        print(f"All reports completed. Success: {success}")
        sys.exit(0 if success else 1)
    
    if args.weekly:
        success = scheduler.run_weekly_report(args.analysis_type)
        sys.exit(0 if success else 1)
    
    if args.monthly:
        success = scheduler.run_monthly_report(args.analysis_type)
        sys.exit(0 if success else 1)
    
    if args.quarterly:
        success = scheduler.run_quarterly_report(args.analysis_type)
        sys.exit(0 if success else 1)
    
    if args.yearly:
        success = scheduler.run_yearly_report(args.analysis_type)
        sys.exit(0 if success else 1)
    
    # Default: show help
    parser.print_help()

if __name__ == "__main__":
    main() 