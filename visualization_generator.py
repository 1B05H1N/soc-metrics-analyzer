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
        
        # Set style for matplotlib
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
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
            # Add explanation text below the charts
            fig.text(0.02, 0.02, explanation, transform=fig.transFigure, 
                    fontsize=9, verticalalignment='bottom', 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8),
                    wrap=True)
        elif position == 'top':
            # Add explanation text at the top (for special cases)
            fig.text(0.02, 0.98, explanation, transform=fig.transFigure, 
                    fontsize=9, verticalalignment='top', 
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.8),
                    wrap=True)
    
    def _create_mttr_mtd_comparison(self) -> str:
        """Create MTTR vs MTD comparison chart"""
        mttr_data = self.metrics_data['mttr']
        mtd_data = self.metrics_data['mtd']
        
        # Increase figure height to accommodate explanation below
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 10))
        
        # MTTR Chart
        categories = ['Calendar Hours', 'Working Hours', 'Calendar Days', 'Working Days']
        mttr_values = [
            mttr_data['mttr_hours'],
            mttr_data['mttr_working_hours'],
            mttr_data['mttr_days'],
            mttr_data['mttr_working_days']
        ]
        
        bars1 = ax1.bar(categories, mttr_values, color='skyblue', alpha=0.7)
        ax1.set_title('Mean Time to Resolution (MTTR)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Time')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars1, mttr_values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.1f}', ha='center', va='bottom')
        
        # MTD Chart
        mtd_values = [
            mtd_data['mtd_hours'],
            mtd_data['mtd_working_hours'],
            mtd_data['mtd_days'],
            mtd_data['mtd_working_days']
        ]
        
        bars2 = ax2.bar(categories, mtd_values, color='lightcoral', alpha=0.7)
        ax2.set_title('Mean Time to Detection (MTD)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Time')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars2, mtd_values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.1f}', ha='center', va='bottom')
        
        # Add explanation text below the charts
        explanation = """EXPLANATION: This chart compares Mean Time to Resolution (MTTR) and Mean Time to Detection (MTD) metrics.
MTTR measures the average time from when an incident is first detected until it is fully resolved.
MTD measures the average time from when an incident occurs until it is first detected by security systems.
Lower values indicate better performance. Working hours exclude weekends and holidays."""
        
        self._add_explanation_text(fig, explanation, 'bottom')
        
        plt.tight_layout()
        
        filename = os.path.join(self.output_dir, 'mttr_mtd_comparison.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _create_resolution_breakdown(self) -> str:
        """Create resolution breakdown pie chart"""
        resolution_data = self.metrics_data['resolution_breakdown']
        
        # Filter out zero values for cleaner visualization
        non_zero_data = {k: v for k, v in resolution_data.items() if v > 0}
        
        if not non_zero_data:
            return None
        
        # Increase figure height to accommodate explanation below
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 10))
        
        # Pie chart
        labels = [k.title() for k in non_zero_data.keys()]
        sizes = list(non_zero_data.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(sizes)))
        
        wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           colors=colors, startangle=90)
        ax1.set_title('Resolution Breakdown', fontsize=14, fontweight='bold')
        
        # Bar chart
        x_pos = np.arange(len(labels))
        bars = ax2.bar(x_pos, sizes, color=colors, alpha=0.7)
        ax2.set_title('Resolution Counts', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Number of Tickets')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(labels, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, value in zip(bars, sizes):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(value), ha='center', va='bottom')
        
        # Add explanation text below the charts
        explanation = """EXPLANATION: This chart shows how security incidents were resolved.
The pie chart displays the percentage distribution of resolution types.
The bar chart shows the actual count of tickets for each resolution type.
Common resolution types include: Done (resolved), False Positive (incorrect alert), 
True Positive (confirmed threat), Duplicate (repeated incident), and Testing (test alerts)."""
        
        self._add_explanation_text(fig, explanation, 'bottom')
        
        plt.tight_layout()
        
        filename = os.path.join(self.output_dir, 'resolution_breakdown.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _create_time_distributions(self) -> str:
        """Create time distribution histograms"""
        time_data = self.metrics_data['time_distributions']
        
        # Increase figure height to accommodate explanation below
        fig, axes = plt.subplots(1, 3, figsize=(18, 10))
        
        # Detection time distribution
        if time_data['detection_times']:
            axes[0].hist(time_data['detection_times'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            axes[0].set_title('Detection Time Distribution', fontweight='bold')
            axes[0].set_xlabel('Hours')
            axes[0].set_ylabel('Frequency')
            axes[0].axvline(np.mean(time_data['detection_times']), color='red', linestyle='--', 
                           label=f'Mean: {np.mean(time_data["detection_times"]):.1f}h')
            axes[0].legend()
        
        # Resolution time distribution
        if time_data['resolution_times']:
            axes[1].hist(time_data['resolution_times'], bins=20, alpha=0.7, color='lightcoral', edgecolor='black')
            axes[1].set_title('Resolution Time Distribution', fontweight='bold')
            axes[1].set_xlabel('Hours')
            axes[1].set_ylabel('Frequency')
            axes[1].axvline(np.mean(time_data['resolution_times']), color='red', linestyle='--',
                           label=f'Mean: {np.mean(time_data["resolution_times"]):.1f}h')
            axes[1].legend()
        
        # Total time distribution
        if time_data['total_times']:
            axes[2].hist(time_data['total_times'], bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
            axes[2].set_title('Total Time Distribution', fontweight='bold')
            axes[2].set_xlabel('Hours')
            axes[2].set_ylabel('Frequency')
            axes[2].axvline(np.mean(time_data['total_times']), color='red', linestyle='--',
                           label=f'Mean: {np.mean(time_data["total_times"]):.1f}h')
            axes[2].legend()
        
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
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _create_weekly_trends(self) -> str:
        """Create weekly trends chart"""
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
            
            # Increase figure height to accommodate explanation below
            fig, axes = plt.subplots(2, 1, figsize=(15, 14))
            
            # Ticket count trend
            axes[0].plot(df['week_label'], df['ticket_count'], marker='o', linewidth=2, markersize=6)
            axes[0].set_title('Weekly Ticket Volume', fontweight='bold')
            axes[0].set_ylabel('Number of Tickets')
            axes[0].tick_params(axis='x', rotation=45)
            axes[0].grid(True, alpha=0.3)
            
            # Time metrics trend
            axes[1].plot(df['week_label'], df['avg_detection_time'], marker='s', label='Detection Time', linewidth=2)
            axes[1].plot(df['week_label'], df['avg_resolution_time'], marker='o', label='Resolution Time', linewidth=2)
            axes[1].plot(df['week_label'], df['avg_total_time'], marker='^', label='Total Time', linewidth=2)
            axes[1].set_title('Weekly Average Times', fontweight='bold')
            axes[1].set_ylabel('Hours')
            axes[1].tick_params(axis='x', rotation=45)
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
            
            # Add explanation text below the charts
            explanation = """EXPLANATION: These charts show trends over time to identify patterns and improvements.
Top Chart: Weekly ticket volume shows incident frequency trends. Spikes may indicate security events or false positive increases.
Bottom Chart: Average response times by week. Declining trends indicate improving efficiency.
Useful for identifying seasonal patterns, security event impacts, and measuring SOC performance improvements over time."""
            
            self._add_explanation_text(fig, explanation, 'bottom')
            
            plt.tight_layout()
            
            filename = os.path.join(self.output_dir, 'weekly_trends.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            print(f"WARNING: Failed to create weekly trends visualization: {e}")
            return None
    
    def _create_percentile_charts(self) -> str:
        """Create percentile comparison charts"""
        percentile_data = self.metrics_data['percentiles']
        
        # Increase figure height to accommodate explanation below
        fig, axes = plt.subplots(1, 3, figsize=(18, 10))
        
        percentiles = [25, 50, 75, 90, 95, 99]
        
        # Detection time percentiles
        detection_values = [percentile_data['detection_time'].get(p/100, 0) for p in percentiles]
        axes[0].bar(range(len(percentiles)), detection_values, color='skyblue', alpha=0.7)
        axes[0].set_title('Detection Time Percentiles', fontweight='bold')
        axes[0].set_xlabel('Percentile')
        axes[0].set_ylabel('Hours')
        axes[0].set_xticks(range(len(percentiles)))
        axes[0].set_xticklabels([f'{p}%' for p in percentiles])
        
        # Resolution time percentiles
        resolution_values = [percentile_data['resolution_time'].get(p/100, 0) for p in percentiles]
        axes[1].bar(range(len(percentiles)), resolution_values, color='lightcoral', alpha=0.7)
        axes[1].set_title('Resolution Time Percentiles', fontweight='bold')
        axes[1].set_xlabel('Percentile')
        axes[1].set_ylabel('Hours')
        axes[1].set_xticks(range(len(percentiles)))
        axes[1].set_xticklabels([f'{p}%' for p in percentiles])
        
        # Total time percentiles
        total_values = [percentile_data['total_time'].get(p/100, 0) for p in percentiles]
        axes[2].bar(range(len(percentiles)), total_values, color='lightgreen', alpha=0.7)
        axes[2].set_title('Total Time Percentiles', fontweight='bold')
        axes[2].set_xlabel('Percentile')
        axes[2].set_ylabel('Hours')
        axes[2].set_xticks(range(len(percentiles)))
        axes[2].set_xticklabels([f'{p}%' for p in percentiles])
        
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
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _create_outlier_analysis(self) -> str:
        """Create outlier analysis visualization"""
        outliers = self.metrics_data.get('outliers', {})
        
        if not outliers.get('detection_outliers') and not outliers.get('resolution_outliers'):
            return None
        
        # Increase figure height to accommodate explanation below
        fig, axes = plt.subplots(1, 2, figsize=(15, 10))
        
        # Detection outliers
        if outliers.get('detection_outliers'):
            detection_data = outliers['detection_outliers'][:10]  # Top 10
            keys = [item['key'] for item in detection_data]
            times = [item['detection_time'] for item in detection_data]
            z_scores = [item['z_score'] for item in detection_data]
            
            bars = axes[0].bar(range(len(keys)), times, color='red', alpha=0.7)
            axes[0].set_title('Top Detection Time Outliers', fontweight='bold')
            axes[0].set_ylabel('Hours')
            axes[0].set_xticks(range(len(keys)))
            axes[0].set_xticklabels(keys, rotation=45, ha='right')
            
            # Add z-score labels
            for i, (bar, z_score) in enumerate(zip(bars, z_scores)):
                axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                            f'Z={z_score:.1f}', ha='center', va='bottom', fontsize=8)
        
        # Resolution outliers
        if outliers.get('resolution_outliers'):
            resolution_data = outliers['resolution_outliers'][:10]  # Top 10
            keys = [item['key'] for item in resolution_data]
            times = [item['resolution_time'] for item in resolution_data]
            z_scores = [item['z_score'] for item in resolution_data]
            
            bars = axes[1].bar(range(len(keys)), times, color='orange', alpha=0.7)
            axes[1].set_title('Top Resolution Time Outliers', fontweight='bold')
            axes[1].set_ylabel('Hours')
            axes[1].set_xticks(range(len(keys)))
            axes[1].set_xticklabels(keys, rotation=45, ha='right')
            
            # Add z-score labels
            for i, (bar, z_score) in enumerate(zip(bars, z_scores)):
                axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                            f'Z={z_score:.1f}', ha='center', va='bottom', fontsize=8)
        
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
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename 