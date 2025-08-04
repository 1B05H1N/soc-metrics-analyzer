#!/usr/bin/env python3
"""
Jira Client using Direct API Calls
Bypasses the jira library for Python 3.13 compatibility
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
from config import Config
import time

class JiraClientDirect:
    """
    Jira client using direct API calls for SOC metrics analysis.
    
    This class provides a direct interface to the Jira REST API for fetching
    issues and their changelog history. It includes caching, rate limiting,
    and comprehensive error handling.
    
    Attributes:
        server (str): Jira server URL
        username (str): Jira username
        api_token (str): Jira API token
        project_key (str): Jira project key
        session (requests.Session): HTTP session with authentication
        _cache (dict): Response cache for performance optimization
        _cache_ttl (int): Cache time-to-live in seconds
        _rate_limit_delay (float): Delay between API requests in seconds
    """
    
    def __init__(self):
        """
        Initialize the Jira client with authentication and configuration.
        
        Raises:
            ValueError: If required environment variables are missing
        """
        load_dotenv()
        self.server = Config.JIRA_SERVER
        self.username = Config.JIRA_USERNAME
        self.api_token = Config.JIRA_API_TOKEN
        self.project_key = Config.PROJECT_KEY
        
        # Create session with authentication
        self.session = requests.Session()
        self.session.auth = (self.username, self.api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Add caching for API responses
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        self._last_request_time = 0
        self._rate_limit_delay = Config.RATE_LIMIT_DELAY
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if available and not expired"""
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_data
            else:
                del self._cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, data: Dict):
        """Cache response with timestamp"""
        self._cache[cache_key] = (data, time.time())
    
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._rate_limit_delay:
            sleep_time = self._rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        self._last_request_time = time.time()
    
    def get_issues(self, max_results: int = 10000, time_period: str = 'ALL_TIME') -> List[Dict]:
        """Get issues from Jira with full changelog, filtered by creation date"""
        print(f"Fetching issues from project {self.project_key}...")
        
        issues = []
        start_at = 0
        total_available = None
        
        # Build JQL query based on time period
        jql = self._build_jql_query(time_period)
        print(f"   Using time-filtered query: {jql}")
        
        while True:
            url = f"{self.server}/rest/api/2/search"
            params = {
                'jql': jql,
                'startAt': start_at,
                'maxResults': 100,  # Jira typically limits to 100 per request
                'expand': 'changelog',
                'fields': 'summary,status,priority,assignee,reporter,created,updated,resolution,resolutiondate,labels,components'
            }
            
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                batch_issues = data.get('issues', [])
                total_available = data.get('total', 0)
                
                print(f"   Found {len(batch_issues)} issues in batch (Total available: {total_available})")
                
                if batch_issues:
                    # Process each issue
                    for issue in batch_issues:
                        processed_issue = self._process_issue(issue)
                        if processed_issue:
                            issues.append(processed_issue)
                    
                    print(f"   SUCCESS: Retrieved {len(batch_issues)} issues (total: {len(issues)})")
                    
                    # Check if we've reached the limit
                    if len(issues) >= max_results:
                        issues = issues[:max_results]
                        print(f"   Reached max results limit: {max_results}")
                        return issues
                    
                    # Check if we've retrieved all available issues
                    if len(issues) >= total_available:
                        print(f"   Retrieved all available issues: {total_available}")
                        break
                    
                    # Check if there are more results in this batch
                    if len(batch_issues) < 100:
                        print(f"   No more results available")
                        break
                    
                    start_at += 100
                    continue
                
            except requests.exceptions.RequestException as e:
                print(f"   ERROR: Error fetching issues: {e}")
                break
        
        print(f"SUCCESS: Retrieved {len(issues)} issues total (out of {total_available} available)")
        return issues
    
    def _build_jql_query(self, time_period: str) -> str:
        """Build JQL query based on time period"""
        base_query = f'project = {self.project_key}'
        
        if time_period == 'ALL_TIME':
            # No time filter for all time
            return f'{base_query} ORDER BY created DESC'
        
        # Get time period configuration
        time_period_config = Config.get_time_period_config(time_period)
        days_back = time_period_config.get('days_back', 30)
        
        # Calculate the date range
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Format dates for JQL (YYYY-MM-DD)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Build JQL with date filter
        jql = f'{base_query} AND created >= "{start_date_str}" AND created <= "{end_date_str}" ORDER BY created DESC'
        
        return jql
    
    def _process_issue(self, issue: Dict) -> Optional[Dict]:
        """Process a single Jira issue"""
        try:
            fields = issue.get('fields', {})
            changelog = issue.get('changelog', {}).get('histories', [])
            
            # Extract basic fields
            key = issue.get('key')
            if not key:
                print(f"WARNING: Issue missing key field")
                return None
                
            summary = fields.get('summary', '')
            status = fields.get('status', {}).get('name', '')
            priority = fields.get('priority', {}).get('name', '')
            assignee = fields.get('assignee', {}).get('displayName', '')
            reporter = fields.get('reporter', {}).get('displayName', '')
            created = fields.get('created', '')
            updated = fields.get('updated', '')
            resolution = fields.get('resolution', {}).get('name', '')
            resolution_date = fields.get('resolutiondate', '')
            
            # Extract labels and components
            labels = fields.get('labels', [])
            components = [comp.get('name', '') for comp in fields.get('components', [])]
            
            # Process changelog to find status transitions
            status_transitions = self._extract_status_transitions(changelog)
            
            # Calculate time metrics
            time_metrics = self._calculate_times(created, updated, resolution_date, status_transitions)
            
            # Determine alert category and severity
            alert_category = self._determine_alert_category(summary, labels, components)
            severity = self._determine_severity(priority, alert_category)
            
            # Check SLA breach
            sla_breach = self._check_sla_breach(time_metrics['total_time'], priority, severity)
            
            # Count escalations
            escalation_count = self._count_escalations(changelog)
            
            # Determine resolution category using dynamic configuration
            resolution_category = self._determine_resolution_category(status, resolution)
            
            return {
                'key': key,
                'summary': summary,
                'status': status,
                'priority': priority,
                'assignee': assignee,
                'reporter': reporter,
                'created': created,
                'updated': updated,
                'resolution': resolution,
                'resolution_date': resolution_date,
                'labels': labels,
                'components': components,
                'alert_category': alert_category,
                'severity': severity,
                'sla_breach': sla_breach,
                'escalation_count': escalation_count,
                'resolution_category': resolution_category,
                'total_time': time_metrics['total_time'],
                'detection_time': time_metrics['detection_time'],
                'resolution_time': time_metrics['resolution_time'],
                'created_date': time_metrics['created_date'],
                'updated_date': time_metrics['updated_date'],
                'resolution_date': time_metrics['resolution_date'],
                'status_transitions': status_transitions
            }
            
        except Exception as e:
            print(f"WARNING: Unexpected error processing issue {issue.get('key', 'UNKNOWN')}: {e}")
            return None
    
    def _extract_status_transitions(self, changelog: List[Dict]) -> List[Dict]:
        """Extract status transitions from changelog"""
        transitions = []
        
        for history in changelog:
            for item in history.get('items', []):
                if item.get('field') == 'status':
                    transitions.append({
                        'from': item.get('fromString', ''),
                        'to': item.get('toString', ''),
                        'date': history.get('created', '')
                    })
        
        return transitions
    
    def _calculate_times(self, created: str, updated: str, resolution_date: str, status_transitions: List[Dict]) -> Dict:
        """Calculate various time metrics using configuration"""
        try:
            created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
            
            # Find when issue was first moved to the configured first action status
            first_action_status = Config.get_first_action_status()
            first_action_time = None
            
            for transition in status_transitions:
                if transition['to'].lower() == first_action_status.lower():
                    first_action_time = datetime.fromisoformat(transition['date'].replace('Z', '+00:00'))
                    break
            
            # Use resolution date if available, otherwise use updated date
            if resolution_date:
                resolution_dt = datetime.fromisoformat(resolution_date.replace('Z', '+00:00'))
            else:
                resolution_dt = updated_dt
            
            # Calculate times
            total_time = (resolution_dt - created_dt).total_seconds() / 3600  # hours
            
            if first_action_time:
                detection_time = (first_action_time - created_dt).total_seconds() / 3600
                resolution_time = (resolution_dt - first_action_time).total_seconds() / 3600
            else:
                detection_time = 0
                resolution_time = total_time
            
            return {
                'total_time': total_time,
                'detection_time': detection_time,
                'resolution_time': resolution_time,
                'created_date': created,
                'updated_date': updated,
                'resolution_date': resolution_date
            }
            
        except Exception as e:
            print(f"WARNING: Error calculating times: {e}")
            return {
                'total_time': 0,
                'detection_time': 0,
                'resolution_time': 0,
                'created_date': created,
                'updated_date': updated,
                'resolution_date': resolution_date
            }
    
    def _determine_alert_category(self, summary: str, labels: List[str], components: List[str]) -> str:
        """Determine alert category based on summary, labels, and components"""
        summary_lower = summary.lower()
        labels_lower = [label.lower() for label in labels]
        components_lower = [comp.lower() for comp in components]
        
        # Check for specific patterns using configuration
        alert_categories = Config.ALERT_CATEGORIES
        
        for category, keywords in alert_categories.items():
            if category == 'general':  # Skip default category
                continue
            if any(keyword in summary_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _determine_severity(self, priority: str, alert_category: str) -> str:
        """Determine severity based on priority and alert category"""
        priority_mapping = Config.PRIORITY_SEVERITY_MAPPING
        return priority_mapping.get(priority, 'Medium')
    
    def _check_sla_breach(self, total_time: float, priority: str, severity: str) -> bool:
        """Check if SLA was breached using configuration thresholds"""
        sla_thresholds = Config.SLA_THRESHOLDS
        threshold = sla_thresholds.get(severity, 24)
        return total_time > threshold
    
    def _count_escalations(self, changelog: List[Dict]) -> int:
        """Count number of escalations (priority changes)"""
        escalation_count = 0
        
        for history in changelog:
            for item in history.get('items', []):
                if item.get('field') == 'priority':
                    escalation_count += 1
        
        return escalation_count

    def _determine_resolution_category(self, status: str, resolution: str) -> str:
        """Determine resolution category using dynamic configuration"""
        try:
            # Get completion statuses from configuration
            completion_statuses = Config.get_completion_statuses()
            resolution_mapping = Config.get_resolution_mapping()
            
            # Check if current status is a completion status (case-insensitive)
            status_lower = status.lower()
            for completion_status in completion_statuses:
                if status_lower == completion_status.lower():
                    # Use resolution mapping if available, otherwise use status
                    return resolution_mapping.get(status, status.lower().replace(' ', '-'))
            
            # Check if resolution field indicates completion (case-insensitive)
            if resolution:
                resolution_lower = resolution.lower()
                for mapped_status, category in resolution_mapping.items():
                    if resolution_lower == mapped_status.lower():
                        return category
            
            # Default to 'done' if status indicates completion but not in mapping
            if status.lower() in ['done', 'closed', 'resolved']:
                return 'done'
            
            # Default to 'open' for non-completed tickets
            return 'open'
            
        except Exception as e:
            print(f"WARNING: Error determining resolution category: {e}")
            return 'unknown'

def main():
    """Test the direct Jira client"""
    try:
        client = JiraClientDirect()
        issues = client.get_issues(max_results=50)  # Limit for testing
        
        print(f"\nRetrieved {len(issues)} issues")
        
        if issues:
            # Show sample data
            sample = issues[0]
            print(f"\nSample Issue:")
            print(f"   Key: {sample['key']}")
            print(f"   Summary: {sample['summary']}")
            print(f"   Status: {sample['status']}")
            print(f"   Priority: {sample['priority']}")
            print(f"   Total Time: {sample['total_time']:.2f} hours")
            print(f"   Detection Time: {sample['detection_time']:.2f} hours")
            print(f"   Resolution Time: {sample['resolution_time']:.2f} hours")
            print(f"   Alert Category: {sample['alert_category']}")
            print(f"   SLA Breach: {sample['sla_breach']}")
        
        return issues
        
    except Exception as e:
        print(f"ERROR: {e}")
        return []

if __name__ == "__main__":
    main() 