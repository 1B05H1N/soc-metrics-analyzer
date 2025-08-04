import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from config import Config

class MetricsCalculator:
    def __init__(self, tickets: List[Dict]):
        self.tickets = tickets
        self.df = self._create_dataframe()
        
        # Memory optimization for large datasets
        if len(self.df) > 1000:
            print(f"INFO: Large dataset detected ({len(self.df)} tickets), optimizing memory usage")
            self._optimize_memory_usage()
    
    def _optimize_memory_usage(self):
        """Optimize memory usage for large datasets"""
        # Convert object columns to category where possible
        categorical_columns = ['status', 'priority', 'severity', 'resolution', 'alert_category']
        for col in categorical_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype('category')
        
        # Convert numeric columns to appropriate dtypes
        numeric_columns = ['detection_time', 'resolution_time', 'total_time', 
                          'detection_time_working_hours', 'resolution_time_working_hours', 
                          'total_time_working_hours']
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        print(f"INFO: Memory optimization complete. DataFrame size: {self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    def _create_dataframe(self) -> pd.DataFrame:
        """Convert tickets to pandas DataFrame for analysis"""
        if not self.tickets:
            print("WARNING: No tickets provided for analysis")
            return pd.DataFrame()
            
        df = pd.DataFrame(self.tickets)
        
        # Validate required columns
        required_columns = ['detection_time', 'resolution_time', 'total_time', 'key', 'status']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"WARNING: Missing required columns: {missing_columns}")
            return pd.DataFrame()
        
        # Filter out tickets without required data
        initial_count = len(df)
        df = df.dropna(subset=['detection_time', 'resolution_time'])
        filtered_count = len(df)
        
        if filtered_count < initial_count:
            print(f"WARNING: Filtered out {initial_count - filtered_count} tickets with missing time data")
        
        # Validate time data quality
        invalid_times = df[
            (df['detection_time'] < 0) | 
            (df['resolution_time'] < 0) | 
            (df['total_time'] < 0) |
            (df['detection_time'] > df['total_time']) |
            (df['resolution_time'] > df['total_time'])
        ]
        
        if not invalid_times.empty:
            print(f"WARNING: Found {len(invalid_times)} tickets with invalid time data")
            df = df.drop(invalid_times.index)
        
        if df.empty:
            print("ERROR: No valid tickets remaining after data validation")
            return df
        
        # Add working hours calculations
        df['detection_time_working_hours'] = df['detection_time'].apply(self._convert_to_working_hours)
        df['resolution_time_working_hours'] = df['resolution_time'].apply(self._convert_to_working_hours)
        df['total_time_working_hours'] = df['total_time'].apply(self._convert_to_working_hours)
        
        print(f"SUCCESS: Created DataFrame with {len(df)} valid tickets")
        return df
    
    def _convert_to_working_hours(self, hours: float) -> float:
        """Convert calendar hours to working hours"""
        if pd.isna(hours) or hours <= 0:
            return 0
        
        # Simple conversion: assume 8 working hours per day, 5 days per week
        days = hours / 24
        working_days = days * (5/7)  # Only count weekdays
        working_hours = working_days * Config.WORKING_HOURS_PER_DAY
        
        return working_hours
    
    def calculate_mttr(self) -> Dict[str, float]:
        """Calculate Mean Time to Resolution (MTTR)"""
        if self.df.empty:
            return {'mttr_hours': 0, 'mttr_working_hours': 0}
        
        # Calculate MTTR in calendar hours
        mttr_hours = self.df['resolution_time'].mean()
        
        # Calculate MTTR in working hours
        mttr_working_hours = self.df['resolution_time_working_hours'].mean()
        
        return {
            'mttr_hours': mttr_hours,
            'mttr_working_hours': mttr_working_hours,
            'mttr_days': mttr_hours / 24,
            'mttr_working_days': mttr_working_hours / Config.WORKING_HOURS_PER_DAY
        }
    
    def calculate_mtd(self) -> Dict[str, float]:
        """Calculate Mean Time to Detection (MTD)"""
        if self.df.empty:
            return {'mtd_hours': 0, 'mtd_working_hours': 0}
        
        # Calculate MTD in calendar hours
        mtd_hours = self.df['detection_time'].mean()
        
        # Calculate MTD in working hours
        mtd_working_hours = self.df['detection_time_working_hours'].mean()
        
        return {
            'mtd_hours': mtd_hours,
            'mtd_working_hours': mtd_working_hours,
            'mtd_days': mtd_hours / 24,
            'mtd_working_days': mtd_working_hours / Config.WORKING_HOURS_PER_DAY
        }
    
    def calculate_resolution_breakdown(self) -> Dict[str, int]:
        """Calculate breakdown by resolution category"""
        resolution_counts = self.df['resolution'].value_counts().to_dict()
        
        # Get resolution mapping from config
        resolution_mapping = Config.get_resolution_mapping()
        
        # Map status names to resolution categories
        mapped_counts = {}
        for status, count in resolution_counts.items():
            category = resolution_mapping.get(status, status.lower().replace(' ', '-'))
            mapped_counts[category] = count
        
        # Ensure all expected categories are represented
        expected_categories = ['expected-activity', 'false-positive', 'true-positive', 'duplicate', 'testing']
        for category in expected_categories:
            if category not in mapped_counts:
                mapped_counts[category] = 0
        
        return mapped_counts
    
    def calculate_time_distributions(self) -> Dict[str, List[float]]:
        """Calculate time distributions for analysis"""
        return {
            'detection_times': self.df['detection_time'].dropna().tolist(),
            'resolution_times': self.df['resolution_time'].dropna().tolist(),
            'total_times': self.df['total_time'].dropna().tolist()
        }
    
    def calculate_percentiles(self) -> Dict[str, Dict[str, float]]:
        """Calculate percentile metrics"""
        percentiles = [25, 50, 75, 90, 95, 99]
        
        return {
            'detection_time': self.df['detection_time'].quantile([p/100 for p in percentiles]).to_dict(),
            'resolution_time': self.df['resolution_time'].quantile([p/100 for p in percentiles]).to_dict(),
            'total_time': self.df['total_time'].quantile([p/100 for p in percentiles]).to_dict()
        }
    
    def calculate_weekly_trends(self) -> Dict[str, List[Dict]]:
        """Calculate weekly trends"""
        if self.df.empty:
            return {'detection_times': [], 'resolution_times': []}
        
        # Convert created_date to datetime with UTC handling
        self.df['created_date'] = pd.to_datetime(self.df['created_date'], utc=True)
        
        # Group by week
        weekly_detection = self.df.groupby(self.df['created_date'].dt.isocalendar().week)['detection_time'].mean()
        weekly_resolution = self.df.groupby(self.df['created_date'].dt.isocalendar().week)['resolution_time'].mean()
        
        return {
            'detection_times': [{'week': int(week), 'avg_time': float(avg)} for week, avg in weekly_detection.items()],
            'resolution_times': [{'week': int(week), 'avg_time': float(avg)} for week, avg in weekly_resolution.items()]
        }
    
    def calculate_summary_statistics(self) -> Dict:
        """Calculate comprehensive summary statistics"""
        if self.df.empty:
            return {}
        
        return {
            'total_tickets': len(self.df),
            'avg_detection_time': self.df['detection_time'].mean(),
            'avg_resolution_time': self.df['resolution_time'].mean(),
            'median_detection_time': self.df['detection_time'].median(),
            'median_resolution_time': self.df['resolution_time'].median(),
            'std_detection_time': self.df['detection_time'].std(),
            'std_resolution_time': self.df['resolution_time'].std(),
            'min_detection_time': self.df['detection_time'].min(),
            'max_detection_time': self.df['detection_time'].max(),
            'min_resolution_time': self.df['resolution_time'].min(),
            'max_resolution_time': self.df['resolution_time'].max()
        }
    
    def get_outliers(self, threshold: float = 2.0) -> Dict[str, List[Dict]]:
        """Identify outliers using IQR method"""
        outliers = {}
        
        for time_type in ['detection_time', 'resolution_time']:
            Q1 = self.df[time_type].quantile(0.25)
            Q3 = self.df[time_type].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            outlier_mask = (self.df[time_type] < lower_bound) | (self.df[time_type] > upper_bound)
            outlier_tickets = self.df[outlier_mask]
            
            outliers[time_type] = []
            for _, ticket in outlier_tickets.iterrows():
                outliers[time_type].append({
                    'key': ticket.get('key', 'Unknown'),
                    'time': ticket[time_type],
                    'summary': ticket.get('summary', ''),
                    'status': ticket.get('status', ''),
                    'priority': ticket.get('priority', '')
                })
        
        return outliers 