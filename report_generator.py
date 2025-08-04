import os
import pandas as pd
from datetime import datetime
from typing import Dict, List
from jinja2 import Template
from config import Config

class ReportGenerator:
    def __init__(self, metrics_data: Dict, visualization_files: List[str]):
        self.metrics_data = metrics_data
        self.visualization_files = visualization_files
        self.output_dir = Config.REPORT_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_html_report(self) -> str:
        """Generate comprehensive HTML report"""
        html_template = self._get_html_template()
        
        # Prepare data for template
        report_data = {
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': self.metrics_data,
            'visualizations': self._prepare_visualization_data(),
            'summary_stats': self._generate_summary_stats(),
            'recommendations': self._generate_recommendations()
        }
        
        # Render template
        template = Template(html_template)
        html_content = template.render(**report_data)
        
        # Save HTML file
        filename = os.path.join(self.output_dir, f'soc_metrics_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def generate_excel_report(self) -> str:
        """Generate Excel report with multiple sheets"""
        filename = os.path.join(self.output_dir, f'soc_metrics_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            self._create_summary_sheet(writer)
            
            # Detailed metrics sheet
            self._create_metrics_sheet(writer)
            
            # Weekly trends sheet
            self._create_trends_sheet(writer)
            
            # Outliers sheet
            self._create_outliers_sheet(writer)
        
        return filename
    
    def _create_summary_sheet(self, writer):
        """Create summary sheet in Excel"""
        summary_data = {
            'Metric': [
                'Total Tickets',
                'Closed Tickets',
                'Open Tickets',
                'MTTR (Hours)',
                'MTTR (Working Hours)',
                'MTTR (Days)',
                'MTD (Hours)',
                'MTD (Working Hours)',
                'MTD (Days)'
            ],
            'Value': [
                self.metrics_data['total_tickets'],
                self.metrics_data['closed_tickets'],
                self.metrics_data['open_tickets'],
                f"{self.metrics_data['mttr']['mttr_hours']:.2f}",
                f"{self.metrics_data['mttr']['mttr_working_hours']:.2f}",
                f"{self.metrics_data['mttr']['mttr_days']:.2f}",
                f"{self.metrics_data['mtd']['mtd_hours']:.2f}",
                f"{self.metrics_data['mtd']['mtd_working_hours']:.2f}",
                f"{self.metrics_data['mtd']['mtd_days']:.2f}"
            ]
        }
        
        df = pd.DataFrame(summary_data)
        df.to_excel(writer, sheet_name='Summary', index=False)
    
    def _create_metrics_sheet(self, writer):
        """Create detailed metrics sheet"""
        # Resolution breakdown
        resolution_data = []
        for category, count in self.metrics_data['resolution_breakdown'].items():
            resolution_data.append({
                'Resolution Category': category.title(),
                'Count': count,
                'Percentage': f"{(count / self.metrics_data['total_tickets'] * 100):.1f}%" if self.metrics_data['total_tickets'] > 0 else "0%"
            })
        
        df_resolution = pd.DataFrame(resolution_data)
        df_resolution.to_excel(writer, sheet_name='Metrics', startrow=0, index=False)
        
        # Percentile data
        percentile_data = []
        percentiles = [25, 50, 75, 90, 95, 99]
        
        for p in percentiles:
            percentile_data.append({
                'Percentile': f"{p}%",
                'Detection Time (Hours)': f"{self.metrics_data['percentiles']['detection_time'].get(p/100, 0):.2f}",
                'Resolution Time (Hours)': f"{self.metrics_data['percentiles']['resolution_time'].get(p/100, 0):.2f}",
                'Total Time (Hours)': f"{self.metrics_data['percentiles']['total_time'].get(p/100, 0):.2f}"
            })
        
        df_percentiles = pd.DataFrame(percentile_data)
        df_percentiles.to_excel(writer, sheet_name='Metrics', startrow=len(resolution_data) + 3, index=False)
    
    def _create_trends_sheet(self, writer):
        """Create weekly trends sheet"""
        if self.metrics_data['weekly_trends']:
            df_trends = pd.DataFrame(self.metrics_data['weekly_trends'])
            df_trends['Week'] = df_trends['year'].astype(str) + '-W' + df_trends['week'].astype(str).str.zfill(2)
            df_trends = df_trends[['Week', 'ticket_count', 'avg_detection_time', 'avg_resolution_time', 'avg_total_time']]
            df_trends.columns = ['Week', 'Ticket Count', 'Avg Detection Time (Hours)', 'Avg Resolution Time (Hours)', 'Avg Total Time (Hours)']
            df_trends.to_excel(writer, sheet_name='Weekly Trends', index=False)
    
    def _create_outliers_sheet(self, writer):
        """Create outliers sheet"""
        outliers = self.metrics_data.get('outliers', {})
        
        if outliers.get('detection_outliers'):
            df_detection = pd.DataFrame(outliers['detection_outliers'])
            df_detection.columns = ['Ticket Key', 'Detection Time (Hours)', 'Z-Score']
            df_detection.to_excel(writer, sheet_name='Outliers', startrow=0, index=False)
        
        if outliers.get('resolution_outliers'):
            df_resolution = pd.DataFrame(outliers['resolution_outliers'])
            df_resolution.columns = ['Ticket Key', 'Resolution Time (Hours)', 'Z-Score']
            df_resolution.to_excel(writer, sheet_name='Outliers', startrow=len(outliers.get('detection_outliers', [])) + 3, index=False)
    
    def _prepare_visualization_data(self) -> List[Dict]:
        """Prepare visualization data for HTML template"""
        viz_data = []
        for file_path in self.visualization_files:
            if file_path and os.path.exists(file_path):
                filename = os.path.basename(file_path)
                title = filename.replace('.png', '').replace('_', ' ').title()
                viz_data.append({
                    'title': title,
                    'filename': filename,
                    'path': file_path
                })
        return viz_data
    
    def _generate_summary_stats(self) -> Dict:
        """Generate summary statistics for the report"""
        return {
            'total_tickets': self.metrics_data['total_tickets'],
            'closed_tickets': self.metrics_data['closed_tickets'],
            'open_tickets': self.metrics_data['open_tickets'],
            'mttr_hours': f"{self.metrics_data['mttr']['mttr_hours']:.1f}",
            'mtd_hours': f"{self.metrics_data['mtd']['mtd_hours']:.1f}",
            'resolution_breakdown': self.metrics_data['resolution_breakdown']
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []
        
        mttr_hours = self.metrics_data['mttr']['mttr_hours']
        mtd_hours = self.metrics_data['mtd']['mtd_hours']
        
        # MTTR recommendations
        if mttr_hours > 24:
            recommendations.append("High MTTR detected. Consider reviewing resolution processes and resource allocation.")
        elif mttr_hours > 8:
            recommendations.append("Moderate MTTR. Focus on process optimization and training.")
        else:
            recommendations.append("Good MTTR performance. Maintain current processes.")
        
        # MTD recommendations
        if mtd_hours > 4:
            recommendations.append("High MTD detected. Review detection processes and alert mechanisms.")
        elif mtd_hours > 2:
            recommendations.append("Moderate MTD. Consider improving initial response procedures.")
        else:
            recommendations.append("Good MTD performance. Maintain current detection processes.")
        
        # Resolution breakdown recommendations
        false_positive_rate = self.metrics_data['resolution_breakdown'].get('false-positive', 0) / max(self.metrics_data['total_tickets'], 1)
        if false_positive_rate > 0.3:
            recommendations.append("High false positive rate. Review alert tuning and detection rules.")
        
        return recommendations
    
    def _get_html_template(self) -> str:
        """Get HTML template for the report"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOC Metrics Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            color: #7f8c8d;
            margin: 5px 0;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            font-size: 1.2em;
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .metrics-table th, .metrics-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .metrics-table th {
            background-color: #3498db;
            color: white;
        }
        .metrics-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .visualization {
            text-align: center;
            margin: 30px 0;
        }
        .visualization img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .recommendations {
            background-color: #e8f4fd;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }
        .recommendations h3 {
            color: #2c3e50;
            margin-top: 0;
        }
        .recommendations ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .recommendations li {
            margin-bottom: 8px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SOC Metrics Report</h1>
            <p>Generated on {{ report_date }}</p>
            <p>Security Operations Center Performance Analysis</p>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <h3>Total Tickets</h3>
                <div class="value">{{ summary_stats.total_tickets }}</div>
            </div>
            <div class="summary-card">
                <h3>Closed Tickets</h3>
                <div class="value">{{ summary_stats.closed_tickets }}</div>
            </div>
            <div class="summary-card">
                <h3>MTTR (Hours)</h3>
                <div class="value">{{ summary_stats.mttr_hours }}</div>
            </div>
            <div class="summary-card">
                <h3>MTD (Hours)</h3>
                <div class="value">{{ summary_stats.mtd_hours }}</div>
            </div>
        </div>

        <div class="section">
            <h2>Key Metrics</h2>
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Mean Time to Resolution (MTTR)</td>
                        <td>{{ metrics.mttr.mttr_hours:.2f }} hours</td>
                        <td>Average time from first action to resolution</td>
                    </tr>
                    <tr>
                        <td>Mean Time to Detection (MTD)</td>
                        <td>{{ metrics.mtd.mtd_hours:.2f }} hours</td>
                        <td>Average time from creation to first action</td>
                    </tr>
                    <tr>
                        <td>Total Tickets Analyzed</td>
                        <td>{{ metrics.total_tickets }}</td>
                        <td>Number of tickets in the analysis period</td>
                    </tr>
                    <tr>
                        <td>Resolution Rate</td>
                        <td>{{ "%.1f"|format((summary_stats.closed_tickets / metrics.total_tickets * 100) if metrics.total_tickets > 0 else 0) }}%</td>
                        <td>Percentage of tickets that have been resolved</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Resolution Breakdown</h2>
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th>Resolution Category</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    {% for category, count in summary_stats.resolution_breakdown.items() %}
                    <tr>
                        <td>{{ category.title() }}</td>
                        <td>{{ count }}</td>
                        <td>{{ "%.1f"|format((count / summary_stats.total_tickets * 100) if summary_stats.total_tickets > 0 else 0) }}%</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        {% for viz in visualizations %}
        <div class="section">
            <h2>{{ viz.title }}</h2>
            <div class="visualization">
                <img src="{{ viz.filename }}" alt="{{ viz.title }}">
            </div>
        </div>
        {% endfor %}

        <div class="section">
            <h2>Recommendations</h2>
            <div class="recommendations">
                <h3>Key Insights and Action Items</h3>
                <ul>
                    {% for recommendation in recommendations %}
                    <li>{{ recommendation }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>

        <div class="footer">
            <p>This report was automatically generated by the SOC Metrics Analysis Tool</p>
            <p>For questions or support, contact the Security Operations Team</p>
        </div>
    </div>
</body>
</html>
        """ 