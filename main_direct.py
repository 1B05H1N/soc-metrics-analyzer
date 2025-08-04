#!/usr/bin/env python3
"""
SOC Metrics Analyzer - Direct Jira Client Version
Main entry point for the SOC Metrics Tool using direct API calls
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Import our modules
from jira_client_direct import JiraClientDirect
from metrics_calculator import MetricsCalculator
from visualization_generator import VisualizationGenerator
from report_generator import ReportGenerator
from excel_report_generator import ExcelReportGenerator
from config import Config

# Configure logging
def setup_logging():
    """Setup structured logging"""
    log_dir = Path("results/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

class SOCMetricsAnalyzer:
    """Main SOC Metrics Analyzer class"""
    
    def __init__(self):
        self.jira_client = None
        self.metrics_calculator = None
        self.visualization_generator = None
        self.report_generator = None
        self.excel_generator = None
        
        # Create output directories
        Path("results/logs").mkdir(parents=True, exist_ok=True)
    
    def run_analysis(self, max_issues: int = 1000, generate_reports: bool = True, 
                    analysis_type: str = 'ALL_TICKETS', time_period: str = 'ALL_TIME',
                    schedule_type: str = None, start_date: datetime = None, 
                    end_date: datetime = None, report_prefix: str = 'soc_metrics') -> bool:
        """Run the complete SOC metrics analysis"""
        print("SOC Metrics Analysis Starting...")
        print("=" * 50)
        
        # Get analysis configuration
        analysis_config = Config.get_analysis_config(analysis_type)
        excluded_statuses = Config.get_excluded_statuses(analysis_type)
        
        # Get time period configuration
        time_period_config = Config.get_time_period_config(time_period)
        
        print(f"Analysis Type: {analysis_config['name']}")
        print(f"Description: {analysis_config['description']}")
        if excluded_statuses:
            print(f"Excluding Statuses: {', '.join(excluded_statuses)}")
        
        print(f"Time Period: {time_period_config['name']}")
        print(f"Description: {time_period_config['description']}")
        if time_period_config['days_back'] > 0:
            print(f"Period: {time_period_config['days_back']} days")
        else:
            print(f"Period: All available data")
        
        if schedule_type:
            schedule_config = Config.get_scheduling_config(schedule_type)
            print(f"Schedule Type: {schedule_config['name']}")
        
        print()
        
        try:
            # Step 1: Connect to Jira and fetch issues
            print("Step 1: Fetching Jira Issues...")
            self.jira_client = JiraClientDirect()
            issues = self.jira_client.get_issues(max_results=max_issues, time_period=time_period)
            
            if not issues:
                print("ERROR: No issues found. Please check your Jira configuration.")
                return False
            
            print(f"SUCCESS: Retrieved {len(issues)} issues for analysis")
            
            # Step 2: Filter issues based on analysis type
            print("Step 2: Filtering Issues...")
            filtered_issues = self._filter_issues(issues, excluded_statuses)
            print(f"SUCCESS: Filtered to {len(filtered_issues)} issues for {analysis_type} analysis")
            
            if not filtered_issues:
                print("ERROR: No issues remain after filtering. Check your exclusion criteria.")
                return False
            
            # Step 3: Calculate metrics
            print("Step 3: Calculating Metrics...")
            self.metrics_calculator = MetricsCalculator(filtered_issues)
            
            # Calculate key metrics
            mttr = self.metrics_calculator.calculate_mttr()
            mtd = self.metrics_calculator.calculate_mtd()
            resolution_breakdown = self.metrics_calculator.calculate_resolution_breakdown()
            time_distributions = self.metrics_calculator.calculate_time_distributions()
            percentiles = self.metrics_calculator.calculate_percentiles()
            weekly_trends = self.metrics_calculator.calculate_weekly_trends()
            summary_stats = self.metrics_calculator.calculate_summary_statistics()
            
            print("SUCCESS: Metrics calculated successfully!")
            print(f"   MTTR: {mttr['mttr_hours']:.2f} hours ({mttr['mttr_working_hours']:.2f} working hours)")
            print(f"   MTD: {mtd['mtd_hours']:.2f} hours ({mtd['mtd_working_hours']:.2f} working hours)")
            print(f"   Resolution breakdown: {resolution_breakdown}")
            
            # Step 4: Generate visualizations (with error handling)
            print("Step 4: Generating Visualizations...")
            try:
                metrics_data = {
                    'mttr': mttr,
                    'mtd': mtd,
                    'resolution_breakdown': resolution_breakdown,
                    'time_distributions': time_distributions,
                    'percentiles': percentiles,
                    'weekly_trends': weekly_trends
                }
                
                self.visualization_generator = VisualizationGenerator(metrics_data)
                generated_files = self.visualization_generator.generate_all_visualizations()
                
                print(f"SUCCESS: Generated {len(generated_files)} visualization files")
                
            except Exception as e:
                print(f"WARNING: Visualization generation failed: {e}")
                print("   Continuing with report generation...")
                generated_files = []
            
            # Step 5: Generate reports
            if generate_reports:
                print("Step 5: Generating Reports...")
                try:
                    # Create summary data
                    completion_statuses = Config.get_completion_statuses()
                    completion_statuses_lower = [status.lower() for status in completion_statuses]
                    
                    summary_data = {
                        'total_tickets': len(filtered_issues),
                        'original_tickets': len(issues),
                        'closed_tickets': len([i for i in filtered_issues if i.get('status', '').lower() in completion_statuses_lower]),
                        'open_tickets': len([i for i in filtered_issues if i.get('status', '').lower() not in completion_statuses_lower]),
                        'analysis_type': analysis_type,
                        'analysis_name': analysis_config['name'],
                        'analysis_description': analysis_config['description'],
                        'excluded_statuses': excluded_statuses,
                        'mttr': mttr,
                        'mtd': mtd,
                        'resolution_breakdown': resolution_breakdown,
                        'weekly_trends': weekly_trends,
                        'summary_statistics': summary_stats,
                        'analysis_period': self._get_analysis_period(schedule_type),
                        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'project_key': os.getenv('PROJECT_KEY', 'YOUR_PROJECT_KEY'),
                        'sla_breaches': sum(1 for issue in filtered_issues if issue.get('sla_breach', False)),
                        'raw_data': filtered_issues[:100]  # Include first 100 tickets as raw data
                    }
                    
                    # Generate reports with appropriate naming
                    if schedule_type:
                        schedule_config = Config.get_scheduling_config(schedule_type)
                        report_prefix = schedule_config['report_prefix']
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        html_report = f'results/reports/{report_prefix}_{analysis_type.lower()}_{timestamp}.html'
                        excel_report = f'results/reports/{report_prefix}_{analysis_type.lower()}_{timestamp}.xlsx'
                        text_report = f'results/reports/{report_prefix}_{analysis_type.lower()}_{timestamp}.txt'
                    else:
                        time_period_config = Config.get_time_period_config(time_period)
                        report_prefix = time_period_config['report_prefix']
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        html_report = f'results/reports/{report_prefix}_{analysis_type.lower()}_{timestamp}.html'
                        excel_report = f'results/reports/{report_prefix}_{analysis_type.lower()}_{timestamp}.xlsx'
                        text_report = f'results/reports/{report_prefix}_{analysis_type.lower()}_{timestamp}.txt'
                    
                    # Generate simple text report first
                    self._generate_text_report(summary_data, text_report)
                    print(f"SUCCESS: Text report generated: {text_report}")
                    
                    # Try to generate HTML report
                    try:
                        visualization_files = []  # Empty list since visualization failed
                        self.report_generator = ReportGenerator(summary_data, visualization_files)
                        html_filename = self.report_generator.generate_html_report()
                        print(f"SUCCESS: HTML report generated: {html_filename}")
                    except Exception as e:
                        print(f"WARNING: HTML report generation failed: {e}")
                    
                    # Try to generate Excel report
                    try:
                        self.excel_generator = ExcelReportGenerator()
                        excel_success = self.excel_generator.create_report(summary_data, excel_report)
                        if excel_success:
                            print(f"SUCCESS: Excel report generated: {excel_report}")
                        else:
                            print(f"WARNING: Excel report generation failed")
                    except Exception as e:
                        print(f"WARNING: Excel report generation failed: {e}")
                    
                except Exception as e:
                    print(f"ERROR: Report generation failed: {e}")
            
            # Step 6: Display summary
            print("Analysis Complete!")
            print("=" * 50)
            print("Key Metrics Summary:")
            print(f"   * Analysis Type: {analysis_config['name']}")
            print(f"   * Total Issues Analyzed: {len(filtered_issues)} (from {len(issues)} total)")
            print(f"   * Mean Time to Resolution (MTTR): {mttr['mttr_hours']:.2f} hours")
            print(f"   * Mean Time to Detection (MTD): {mtd['mtd_hours']:.2f} hours")
            print(f"   * Resolution Breakdown: {resolution_breakdown}")
            print(f"   * SLA Breaches: {sum(1 for issue in filtered_issues if issue.get('sla_breach', False))}")
            
            # Show sample issues
            print("Sample Issues Analyzed:")
            for i, issue in enumerate(filtered_issues[:5]):
                print(f"   {i+1}. {issue['key']}: {issue['summary'][:50]}...")
                print(f"      Status: {issue['status']}, Priority: {issue['priority']}")
                print(f"      Total Time: {issue['total_time']:.2f}h, Detection: {issue['detection_time']:.2f}h")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Error during analysis: {e}")
            return False
    
    def _filter_issues(self, issues: list, excluded_statuses: list) -> list:
        """Filter issues based on excluded statuses"""
        if not excluded_statuses:
            return issues
        
        filtered_issues = []
        excluded_count = 0
        
        for issue in issues:
            if issue.get('status') not in excluded_statuses:
                filtered_issues.append(issue)
            else:
                excluded_count += 1
        
        print(f"   Filtered out {excluded_count} issues with excluded statuses: {', '.join(excluded_statuses)}")
        return filtered_issues
    
    def _get_analysis_period(self, schedule_type: str) -> str:
        """Get analysis period description"""
        if schedule_type:
            schedule_config = Config.get_scheduling_config(schedule_type)
            return f"Last {schedule_config['days_back']} days"
        else:
            return "Last 30 days"
    
    def _generate_text_report(self, summary_data: dict, filename: str):
        """Generates a simple text report."""
        try:
            completion_statuses = Config.get_completion_statuses()
            resolution_mapping = Config.get_resolution_mapping()
            
            with open(filename, 'w') as f:
                f.write("SOC Metrics Report\n")
                f.write("=" * 20 + "\n")
                f.write(f"Analysis Type: {summary_data.get('analysis_name', 'Unknown')}\n")
                f.write(f"Description: {summary_data.get('analysis_description', 'Unknown')}\n")
                f.write(f"Excluded Statuses: {', '.join(summary_data.get('excluded_statuses', []))}\n")
                f.write(f"Analysis Period: {summary_data.get('analysis_period', 'Unknown')}\n")
                f.write(f"Generated At: {summary_data.get('generated_at', 'Unknown')}\n")
                f.write(f"Project Key: {summary_data.get('project_key', 'Unknown')}\n")
                f.write(f"Total Issues Analyzed: {summary_data.get('total_tickets', 0)}\n")
                f.write(f"Original Issues: {summary_data.get('original_tickets', 0)}\n")
                f.write(f"Closed Issues: {summary_data.get('closed_tickets', 0)}\n")
                f.write(f"Open Issues: {summary_data.get('open_tickets', 0)}\n")
                f.write(f"SLA Breaches: {summary_data.get('sla_breaches', 0)}\n")
                f.write(f"\nCompletion Statuses (from config): {', '.join(completion_statuses)}\n")
                f.write(f"Resolution Mapping (from config): {resolution_mapping}\n")
                f.write("\nKey Metrics:\n")
                
                # Safely extract MTTR and MTD data
                mttr_data = summary_data.get('mttr', {})
                mtd_data = summary_data.get('mtd', {})
                
                if isinstance(mttr_data, dict):
                    f.write(f"   MTTR: {mttr_data.get('mttr_hours', 0):.2f} hours ({mttr_data.get('mttr_working_hours', 0):.2f} working hours)\n")
                else:
                    f.write(f"   MTTR: N/A\n")
                
                if isinstance(mtd_data, dict):
                    f.write(f"   MTD: {mtd_data.get('mtd_hours', 0):.2f} hours ({mtd_data.get('mtd_working_hours', 0):.2f} working hours)\n")
                else:
                    f.write(f"   MTD: N/A\n")
                
                f.write(f"   Resolution Breakdown: {summary_data.get('resolution_breakdown', {})}\n")
                f.write(f"   SLA Breaches: {summary_data.get('sla_breaches', 0)}\n")
                
                f.write("\nSummary Statistics:\n")
                summary_stats = summary_data.get('summary_statistics', {})
                if isinstance(summary_stats, dict):
                    for key, value in summary_stats.items():
                        f.write(f"   {key}: {value}\n")
                else:
                    f.write("   No summary statistics available\n")
                
                f.write("\nWeekly Trends:\n")
                weekly_trends = summary_data.get('weekly_trends', [])
                if isinstance(weekly_trends, list):
                    for trend in weekly_trends:
                        if isinstance(trend, dict):
                            f.write(f"   {trend.get('date', 'Unknown')}: {trend.get('mttr_hours', 0):.2f} hours\n")
                        else:
                            f.write(f"   Invalid trend data: {trend}\n")
                else:
                    f.write("   No weekly trends available\n")
                
                f.write("\nRaw Data (first 100 issues):\n")
                raw_data = summary_data.get('raw_data', [])
                if isinstance(raw_data, list):
                    for issue in raw_data[:10]:  # Limit to first 10 for readability
                        if isinstance(issue, dict):
                            f.write(f"   {issue.get('key', 'Unknown')}: {issue.get('summary', 'No summary')}\n")
                            f.write(f"      Status: {issue.get('status', 'Unknown')}, Priority: {issue.get('priority', 'Unknown')}\n")
                            f.write(f"      Total Time: {issue.get('total_time', 0):.2f}h, Detection: {issue.get('detection_time', 0):.2f}h\n")
                        else:
                            f.write(f"   Invalid issue data: {issue}\n")
                else:
                    f.write("   No raw data available\n")
                    
        except Exception as e:
            print(f"ERROR: Failed to generate text report: {e}")
            # Create a minimal fallback report
            with open(filename, 'w') as f:
                f.write("SOC Metrics Report\n")
                f.write("=" * 20 + "\n")
                f.write("Report generation failed due to data format issues.\n")
                f.write(f"Error: {e}\n")

    def run_both_analyses(self, max_issues: int = 1000, generate_reports: bool = True,
                          time_period: str = 'ALL_TIME', schedule_type: str = None, 
                          start_date: datetime = None, end_date: datetime = None, 
                          report_prefix: str = 'soc_metrics'):
        """Run both types of analysis"""
        print("Running Both Analysis Types...")
        print("=" * 50)
        
        results = {}
        
        # Run ALL_TICKETS analysis
        print("\n" + "="*30)
        print("ANALYSIS 1: All Tickets")
        print("="*30)
        success1 = self.run_analysis(max_issues, generate_reports, 'ALL_TICKETS', time_period,
                                   schedule_type, start_date, end_date, report_prefix)
        results['ALL_TICKETS'] = success1
        
        # Run EXCLUDE_TESTING_DUPLICATES analysis
        print("\n" + "="*30)
        print("ANALYSIS 2: Production Tickets (Excluding Testing/Duplicates)")
        print("="*30)
        success2 = self.run_analysis(max_issues, generate_reports, 'EXCLUDE_TESTING_DUPLICATES', time_period,
                                   schedule_type, start_date, end_date, report_prefix)
        results['EXCLUDE_TESTING_DUPLICATES'] = success2
        
        # Summary
        print("\n" + "="*50)
        print("ANALYSIS SUMMARY")
        print("="*50)
        print(f"All Tickets Analysis: {'SUCCESS' if success1 else 'FAILED'}")
        print(f"Production Tickets Analysis: {'SUCCESS' if success2 else 'FAILED'}")
        
        return all(results.values())

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='SOC Metrics Analyzer')
    parser.add_argument('--max-issues', type=int, default=1000, 
                       help='Maximum number of issues to analyze (default: 1000)')
    parser.add_argument('--no-reports', action='store_true',
                       help='Skip report generation')
    parser.add_argument('--test', action='store_true',
                       help='Run in test mode with limited issues')
    parser.add_argument('--analysis-type', choices=['ALL_TICKETS', 'EXCLUDE_TESTING_DUPLICATES', 'BOTH'],
                       default='BOTH', help='Type of analysis to run (default: BOTH)')
    parser.add_argument('--time-period', choices=Config.get_all_time_periods(),
                       default='ALL_TIME', help='Time period for analysis (default: ALL_TIME)')
    parser.add_argument('--schedule-type', choices=['WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY'],
                       help='Schedule type for automated reporting')
    parser.add_argument('--report-prefix', default='soc_metrics',
                       help='Prefix for report filenames')
    
    args = parser.parse_args()
    
    # Validate configuration
    if not Config.validate_config():
        logger.error("Configuration validation failed")
        sys.exit(1)
    
    # Validate input parameters
    if args.max_issues <= 0:
        logger.error("max-issues must be greater than 0")
        sys.exit(1)
    
    if args.max_issues > 50000:
        logger.warning("max-issues is very large, this may take a long time")
    
    # Create analyzer instance
    analyzer = SOCMetricsAnalyzer()
    
    # Set max issues for test mode
    max_issues = 50 if args.test else args.max_issues
    
    logger.info(f"Starting analysis with max_issues={max_issues}, analysis_type={args.analysis_type}, time_period={args.time_period}")
    
    # Run analysis based on type
    if args.analysis_type == 'BOTH':
        success = analyzer.run_both_analyses(
            max_issues=max_issues,
            generate_reports=not args.no_reports,
            time_period=args.time_period,
            schedule_type=args.schedule_type,
            report_prefix=args.report_prefix
        )
    else:
        success = analyzer.run_analysis(
            max_issues=max_issues,
            generate_reports=not args.no_reports,
            analysis_type=args.analysis_type,
            time_period=args.time_period,
            schedule_type=args.schedule_type,
            report_prefix=args.report_prefix
        )
    
    if success:
        logger.info("SOC Metrics Analysis completed successfully!")
        print("Check the 'results/reports' directory for generated files.")
    else:
        logger.error("Analysis failed")
        print("ERROR: Analysis failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 