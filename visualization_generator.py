import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List
import os
from config import Config

class VisualizationGenerator:
    def __init__(self, metrics_data: Dict):
        self.metrics_data = metrics_data
        self.output_dir = Config.REPORT_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set professional style for matplotlib
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Professional color scheme
        self.colors = {
            'primary': '#2E86AB',      # Professional blue
            'secondary': '#A23B72',    # Professional purple
            'success': '#F18F01',      # Professional orange
            'warning': '#C73E1D',      # Professional red
            'info': '#6B8E23',         # Professional green
            'light_blue': '#87CEEB',   # Light blue
            'light_coral': '#F08080',  # Light coral
            'light_green': '#90EE90',  # Light green
            'light_orange': '#FFB347', # Light orange
            'light_red': '#FF6B6B',    # Light red
            'gray': '#808080',         # Gray
            'light_gray': '#D3D3D3'    # Light gray
        }
        
        # Set font properties for better readability
        plt.rcParams['font.size'] = 10
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
        plt.rcParams['figure.titlesize'] = 16
    
    def generate_all_visualizations(self) -> List[str]:
        """Generate all visualizations and return file paths"""
        generated_files = []
        
        # Generate each visualization
        files = [
            self._create_mttr_mtd_comparison(),
            self._create_resolution_breakdown(),
            self._create_time_distributions(),
            self._create_weekly_trends(),
            self._create_percentile_charts(),
            self._create_outlier_analysis()
        ]
        
        generated_files.extend([f for f in files if f])
        return generated_files
    
    def _add_explanation_text(self, fig, explanation: str, position: str = 'bottom'):
        """Add explanation text to the figure below the charts"""
        if position == 'bottom':
            # Add explanation text below the charts with professional styling
            fig.text(0.02, 0.02, explanation, transform=fig.transFigure, 
                    fontsize=9, verticalalignment='bottom', 
                    bbox=dict(boxstyle='round,pad=0.8', 
                             facecolor='#F8F9FA', 
                             edgecolor='#DEE2E6',
                             alpha=0.95),
                    wrap=True)
        elif position == 'top':
            # Add explanation text at the top (for special cases)
            fig.text(0.02, 0.98, explanation, transform=fig.transFigure, 
                    fontsize=9, verticalalignment='top', 
                    bbox=dict(boxstyle='round,pad=0.8', 
                             facecolor='#E3F2FD', 
                             edgecolor='#BBDEFB',
                             alpha=0.95),
                    wrap=True)
    
    def _create_mttr_mtd_comparison(self) -> str:
        """Create MTTR vs MTD comparison chart with enhanced styling"""
        mttr_data = self.metrics_data['mttr']
        mtd_data = self.metrics_data['mtd']
        
        # Create figure with enhanced styling
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('SOC Performance Metrics Comparison', fontsize=16, fontweight='bold', y=0.95)
        
        # MTTR Chart
        categories = ['Calendar\nHours', 'Working\nHours', 'Calendar\nDays', 'Working\nDays']
        mttr_values = [
            mttr_data['mttr_hours'],
            mttr_data['mttr_working_hours'],
            mttr_data['mttr_days'],
            mttr_data['mttr_working_days']
        ]
        
        bars1 = ax1.bar(categories, mttr_values, color=self.colors['primary'], alpha=0.8, edgecolor='white', linewidth=1)
        ax1.set_title('Mean Time to Resolution (MTTR)', fontsize=14, fontweight='bold', pad=20)
        ax1.set_ylabel('Time (Hours/Days)', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars with enhanced styling
        for bar, value in zip(bars1, mttr_values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2, height + max(mttr_values) * 0.02,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        # MTD Chart
        mtd_values = [
            mtd_data['mtd_hours'],
            mtd_data['mtd_working_hours'],
            mtd_data['mtd_days'],
            mtd_data['mtd_working_days']
        ]
        
        bars2 = ax2.bar(categories, mtd_values, color=self.colors['secondary'], alpha=0.8, edgecolor='white', linewidth=1)
        ax2.set_title('Mean Time to Detection (MTD)', fontsize=14, fontweight='bold', pad=20)
        ax2.set_ylabel('Time (Hours/Days)', fontweight='bold')
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars with enhanced styling
        for bar, value in zip(bars2, mtd_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + max(mtd_values) * 0.02,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        # Add explanation text below the charts
        explanation = """EXPLANATION: This chart compares Mean Time to Resolution (MTTR) and Mean Time to Detection (MTD) metrics.
MTTR measures the average time from when an incident is first detected until it is fully resolved.
MTD measures the average time from when an incident occurs until it is first detected by security systems.
Lower values indicate better performance. Working hours exclude weekends and holidays."""
        
        self._add_explanation_text(fig, explanation, 'bottom')
        
        plt.tight_layout()
        
        filename = os.path.join(self.output_dir, 'mttr_mtd_comparison.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return filename
    
    def _create_resolution_breakdown(self) -> str:
        """Create resolution breakdown pie chart with enhanced styling"""
        resolution_data = self.metrics_data['resolution_breakdown']
        
        # Filter out zero values for cleaner visualization
        non_zero_data = {k: v for k, v in resolution_data.items() if v > 0}
        
        if not non_zero_data:
            return None
        
        # Create figure with enhanced styling
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('Security Incident Resolution Analysis', fontsize=16, fontweight='bold', y=0.95)
        
        # Professional color palette
        colors = [self.colors['primary'], self.colors['secondary'], self.colors['success'], 
                 self.colors['warning'], self.colors['info'], self.colors['light_blue']]
        
        # Pie chart
        labels = [k.replace('-', ' ').title() for k in non_zero_data.keys()]
        sizes = list(non_zero_data.values())
        
        wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           colors=colors[:len(sizes)], startangle=90,
                                           textprops={'fontsize': 10, 'fontweight': 'bold'})
        ax1.set_title('Resolution Distribution (%)', fontsize=14, fontweight='bold', pad=20)
        
        # Bar chart
        x_pos = np.arange(len(labels))
        bars = ax2.bar(x_pos, sizes, color=colors[:len(sizes)], alpha=0.8, 
                      edgecolor='white', linewidth=1)
        ax2.set_title('Resolution Counts', fontsize=14, fontweight='bold', pad=20)
        ax2.set_ylabel('Number of Incidents', fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(labels, rotation=45, ha='right', fontsize=10)
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars with enhanced styling
        for bar, value in zip(bars, sizes):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + max(sizes) * 0.02,
                    str(value), ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        # Add explanation text below the charts
        explanation = """EXPLANATION: This chart shows how security incidents were resolved.
The pie chart displays the percentage distribution of resolution types.
The bar chart shows the actual count of tickets for each resolution type.
Common resolution types include: Done (resolved), False Positive (incorrect alert), 
True Positive (confirmed threat), Duplicate (repeated incident), and Testing (test alerts)."""
        
        self._add_explanation_text(fig, explanation, 'bottom')
        
        plt.tight_layout()
        
        filename = os.path.join(self.output_dir, 'resolution_breakdown.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return filename
    
    def _create_time_distributions(self) -> str:
        """Create time distribution histograms with enhanced styling"""
        time_data = self.metrics_data['time_distributions']
        
        # Create figure with enhanced styling
        fig, axes = plt.subplots(1, 3, figsize=(18, 8))
        fig.suptitle('Response Time Distribution Analysis', fontsize=16, fontweight='bold', y=0.95)
        
        # Detection time distribution
        if time_data['detection_times']:
            axes[0].hist(time_data['detection_times'], bins=20, alpha=0.7, 
                        color=self.colors['light_blue'], edgecolor='white', linewidth=1)
            axes[0].set_title('Detection Time Distribution', fontweight='bold', pad=20)
            axes[0].set_xlabel('Time (Hours)', fontweight='bold')
            axes[0].set_ylabel('Number of Incidents', fontweight='bold')
            mean_detection = np.mean(time_data['detection_times'])
            axes[0].axvline(mean_detection, color=self.colors['warning'], linestyle='--', 
                           linewidth=2, label=f'Mean: {mean_detection:.1f}h')
            axes[0].legend(fontsize=10)
            axes[0].grid(axis='y', alpha=0.3, linestyle='--')
        
        # Resolution time distribution
        if time_data['resolution_times']:
            axes[1].hist(time_data['resolution_times'], bins=20, alpha=0.7, 
                        color=self.colors['light_coral'], edgecolor='white', linewidth=1)
            axes[1].set_title('Resolution Time Distribution', fontweight='bold', pad=20)
            axes[1].set_xlabel('Time (Hours)', fontweight='bold')
            axes[1].set_ylabel('Number of Incidents', fontweight='bold')
            mean_resolution = np.mean(time_data['resolution_times'])
            axes[1].axvline(mean_resolution, color=self.colors['warning'], linestyle='--',
                           linewidth=2, label=f'Mean: {mean_resolution:.1f}h')
            axes[1].legend(fontsize=10)
            axes[1].grid(axis='y', alpha=0.3, linestyle='--')
        
        # Total time distribution
        if time_data['total_times']:
            axes[2].hist(time_data['total_times'], bins=20, alpha=0.7, 
                        color=self.colors['light_green'], edgecolor='white', linewidth=1)
            axes[2].set_title('Total Time Distribution', fontweight='bold', pad=20)
            axes[2].set_xlabel('Time (Hours)', fontweight='bold')
            axes[2].set_ylabel('Number of Incidents', fontweight='bold')
            mean_total = np.mean(time_data['total_times'])
            axes[2].axvline(mean_total, color=self.colors['warning'], linestyle='--',
                           linewidth=2, label=f'Mean: {mean_total:.1f}h')
            axes[2].legend(fontsize=10)
            axes[2].grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add explanation text below the charts
        explanation = """EXPLANATION: These histograms show the distribution of time metrics across all incidents.
Detection Time: Time from incident occurrence to first detection by security systems.
Resolution Time: Time from first detection to complete resolution of the incident.
Total Time: Complete time from incident occurrence to resolution.
The red dashed line shows the mean value. Lower times indicate better performance.
Wide distributions suggest inconsistent response times, while narrow distributions indicate consistent performance."""
        
        self._add_explanation_text(fig, explanation, 'bottom')
        
        plt.tight_layout()
        
        filename = os.path.join(self.output_dir, 'time_distributions.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return filename
    
    def _create_weekly_trends(self) -> str:
        """Create weekly trends chart with enhanced styling"""
        weekly_data = self.metrics_data['weekly_trends']
        
        if not weekly_data:
            return None
        
        try:
            df = pd.DataFrame(weekly_data)
            
            # Check if required columns exist
            if 'year' not in df.columns or 'week' not in df.columns:
                print("WARNING: Weekly trends data missing required columns (year, week)")
                return None
                
            df['week_label'] = df['year'].astype(str) + '-W' + df['week'].astype(str).str.zfill(2)
            
            # Create figure with enhanced styling
            fig, axes = plt.subplots(2, 1, figsize=(16, 12))
            fig.suptitle('SOC Performance Trends Over Time', fontsize=16, fontweight='bold', y=0.95)
            
            # Ticket count trend
            axes[0].plot(df['week_label'], df['ticket_count'], marker='o', linewidth=3, 
                        markersize=8, color=self.colors['primary'], alpha=0.8)
            axes[0].set_title('Weekly Incident Volume', fontweight='bold', pad=20)
            axes[0].set_ylabel('Number of Incidents', fontweight='bold')
            axes[0].tick_params(axis='x', rotation=45)
            axes[0].grid(True, alpha=0.3, linestyle='--')
            axes[0].set_facecolor('#F8F9FA')
            
            # Time metrics trend
            axes[1].plot(df['week_label'], df['avg_detection_time'], marker='s', 
                        label='Detection Time', linewidth=3, markersize=8, color=self.colors['primary'])
            axes[1].plot(df['week_label'], df['avg_resolution_time'], marker='o', 
                        label='Resolution Time', linewidth=3, markersize=8, color=self.colors['secondary'])
            axes[1].plot(df['week_label'], df['avg_total_time'], marker='^', 
                        label='Total Time', linewidth=3, markersize=8, color=self.colors['success'])
            axes[1].set_title('Weekly Average Response Times', fontweight='bold', pad=20)
            axes[1].set_ylabel('Time (Hours)', fontweight='bold')
            axes[1].tick_params(axis='x', rotation=45)
            axes[1].legend(fontsize=10, loc='upper right')
            axes[1].grid(True, alpha=0.3, linestyle='--')
            axes[1].set_facecolor('#F8F9FA')
            
            # Add explanation text below the charts
            explanation = """EXPLANATION: These charts show trends over time to identify patterns and improvements.
Top Chart: Weekly ticket volume shows incident frequency trends. Spikes may indicate security events or false positive increases.
Bottom Chart: Average response times by week. Declining trends indicate improving efficiency.
Useful for identifying seasonal patterns, security event impacts, and measuring SOC performance improvements over time."""
            
            self._add_explanation_text(fig, explanation, 'bottom')
            
            plt.tight_layout()
            
            filename = os.path.join(self.output_dir, 'weekly_trends.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return filename
            
        except Exception as e:
            print(f"WARNING: Failed to create weekly trends visualization: {e}")
            return None
    
    def _create_percentile_charts(self) -> str:
        """Create percentile comparison charts with enhanced styling"""
        percentile_data = self.metrics_data['percentiles']
        
        # Create figure with enhanced styling
        fig, axes = plt.subplots(1, 3, figsize=(18, 8))
        fig.suptitle('Response Time Performance Percentiles', fontsize=16, fontweight='bold', y=0.95)
        
        percentiles = [25, 50, 75, 90, 95, 99]
        
        # Detection time percentiles
        detection_values = [percentile_data['detection_time'].get(p/100, 0) for p in percentiles]
        bars1 = axes[0].bar(range(len(percentiles)), detection_values, 
                           color=self.colors['light_blue'], alpha=0.8, 
                           edgecolor='white', linewidth=1)
        axes[0].set_title('Detection Time Percentiles', fontweight='bold', pad=20)
        axes[0].set_xlabel('Percentile', fontweight='bold')
        axes[0].set_ylabel('Time (Hours)', fontweight='bold')
        axes[0].set_xticks(range(len(percentiles)))
        axes[0].set_xticklabels([f'{p}%' for p in percentiles], fontsize=10)
        axes[0].grid(axis='y', alpha=0.3, linestyle='--')
        
        # Resolution time percentiles
        resolution_values = [percentile_data['resolution_time'].get(p/100, 0) for p in percentiles]
        bars2 = axes[1].bar(range(len(percentiles)), resolution_values, 
                           color=self.colors['light_coral'], alpha=0.8, 
                           edgecolor='white', linewidth=1)
        axes[1].set_title('Resolution Time Percentiles', fontweight='bold', pad=20)
        axes[1].set_xlabel('Percentile', fontweight='bold')
        axes[1].set_ylabel('Time (Hours)', fontweight='bold')
        axes[1].set_xticks(range(len(percentiles)))
        axes[1].set_xticklabels([f'{p}%' for p in percentiles], fontsize=10)
        axes[1].grid(axis='y', alpha=0.3, linestyle='--')
        
        # Total time percentiles
        total_values = [percentile_data['total_time'].get(p/100, 0) for p in percentiles]
        bars3 = axes[2].bar(range(len(percentiles)), total_values, 
                           color=self.colors['light_green'], alpha=0.8, 
                           edgecolor='white', linewidth=1)
        axes[2].set_title('Total Time Percentiles', fontweight='bold', pad=20)
        axes[2].set_xlabel('Percentile', fontweight='bold')
        axes[2].set_ylabel('Time (Hours)', fontweight='bold')
        axes[2].set_xticks(range(len(percentiles)))
        axes[2].set_xticklabels([f'{p}%' for p in percentiles], fontsize=10)
        axes[2].grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bars, values in [(bars1, detection_values), (bars2, resolution_values), (bars3, total_values)]:
            for bar, value in zip(bars, values):
                height = bar.get_height()
                if height > 0:
                    bar.axes.text(bar.get_x() + bar.get_width()/2, height + max(values) * 0.02,
                                f'{value:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # Add explanation text below the charts
        explanation = """EXPLANATION: These percentile charts show the distribution of response times across different performance levels.
25th percentile: 25% of incidents were resolved faster than this time (good performance).
50th percentile (median): Half of incidents were resolved faster than this time.
75th percentile: 75% of incidents were resolved faster than this time.
90th/95th/99th percentiles: Show the worst-case scenarios and outliers.
Lower values across all percentiles indicate better overall performance and consistency."""
        
        self._add_explanation_text(fig, explanation, 'bottom')
        
        plt.tight_layout()
        
        filename = os.path.join(self.output_dir, 'percentile_charts.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return filename
    
    def _create_outlier_analysis(self) -> str:
        """Create outlier analysis visualization with enhanced styling"""
        outliers = self.metrics_data.get('outliers', {})
        
        if not outliers.get('detection_outliers') and not outliers.get('resolution_outliers'):
            return None
        
        # Create figure with enhanced styling
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('Response Time Outlier Analysis', fontsize=16, fontweight='bold', y=0.95)
        
        # Detection outliers
        if outliers.get('detection_outliers'):
            detection_data = outliers['detection_outliers'][:10]  # Top 10
            keys = [item['key'] for item in detection_data]
            times = [item['detection_time'] for item in detection_data]
            z_scores = [item['z_score'] for item in detection_data]
            
            bars1 = axes[0].bar(range(len(keys)), times, color=self.colors['light_red'], 
                               alpha=0.8, edgecolor='white', linewidth=1)
            axes[0].set_title('Top Detection Time Outliers', fontweight='bold', pad=20)
            axes[0].set_ylabel('Time (Hours)', fontweight='bold')
            axes[0].set_xticks(range(len(keys)))
            axes[0].set_xticklabels(keys, rotation=45, ha='right', fontsize=9)
            axes[0].grid(axis='y', alpha=0.3, linestyle='--')
            
            # Add z-score labels
            for i, (bar, z_score) in enumerate(zip(bars1, z_scores)):
                height = bar.get_height()
                axes[0].text(bar.get_x() + bar.get_width()/2, height + max(times) * 0.02,
                            f'Z={z_score:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
        
        # Resolution outliers
        if outliers.get('resolution_outliers'):
            resolution_data = outliers['resolution_outliers'][:10]  # Top 10
            keys = [item['key'] for item in resolution_data]
            times = [item['resolution_time'] for item in resolution_data]
            z_scores = [item['z_score'] for item in resolution_data]
            
            bars2 = axes[1].bar(range(len(keys)), times, color=self.colors['light_orange'], 
                               alpha=0.8, edgecolor='white', linewidth=1)
            axes[1].set_title('Top Resolution Time Outliers', fontweight='bold', pad=20)
            axes[1].set_ylabel('Time (Hours)', fontweight='bold')
            axes[1].set_xticks(range(len(keys)))
            axes[1].set_xticklabels(keys, rotation=45, ha='right', fontsize=9)
            axes[1].grid(axis='y', alpha=0.3, linestyle='--')
            
            # Add z-score labels
            for i, (bar, z_score) in enumerate(zip(bars2, z_scores)):
                height = bar.get_height()
                axes[1].text(bar.get_x() + bar.get_width()/2, height + max(times) * 0.02,
                            f'Z={z_score:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
        
        # Add explanation text below the charts
        explanation = """EXPLANATION: This chart identifies incidents with unusually long detection or resolution times.
Outliers are calculated using Z-scores (standard deviations from the mean).
Z-scores > 2 indicate significant outliers that may need investigation.
High detection times may indicate security tool failures or missed threats.
High resolution times may indicate complex incidents or resource constraints.
Review these outliers to identify systemic issues or areas for improvement."""
        
        self._add_explanation_text(fig, explanation, 'bottom')
        
        plt.tight_layout()
        
        filename = os.path.join(self.output_dir, 'outlier_analysis.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return filename 