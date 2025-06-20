#!/usr/bin/env python3
"""
N8N Workflow Intelligent Renamer
Analyzes workflow JSON files and generates meaningful names based on content.
"""

import json
import os
import re
import glob
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import argparse

class WorkflowRenamer:
    """Intelligent workflow file renamer based on content analysis."""
    
    def __init__(self, workflows_dir: str = "workflows", dry_run: bool = True):
        self.workflows_dir = workflows_dir
        self.dry_run = dry_run
        self.rename_actions = []
        self.errors = []
        
        # Common service mappings for cleaner names
        self.service_mappings = {
            'n8n-nodes-base.webhook': 'Webhook',
            'n8n-nodes-base.cron': 'Cron',
            'n8n-nodes-base.httpRequest': 'HTTP',
            'n8n-nodes-base.gmail': 'Gmail',
            'n8n-nodes-base.googleSheets': 'GoogleSheets',
            'n8n-nodes-base.slack': 'Slack',
            'n8n-nodes-base.telegram': 'Telegram',
            'n8n-nodes-base.discord': 'Discord',
            'n8n-nodes-base.airtable': 'Airtable',
            'n8n-nodes-base.notion': 'Notion',
            'n8n-nodes-base.stripe': 'Stripe',
            'n8n-nodes-base.hubspot': 'Hubspot',
            'n8n-nodes-base.salesforce': 'Salesforce',
            'n8n-nodes-base.shopify': 'Shopify',
            'n8n-nodes-base.wordpress': 'WordPress',
            'n8n-nodes-base.mysql': 'MySQL',
            'n8n-nodes-base.postgres': 'Postgres',
            'n8n-nodes-base.mongodb': 'MongoDB',
            'n8n-nodes-base.redis': 'Redis',
            'n8n-nodes-base.aws': 'AWS',
            'n8n-nodes-base.googleDrive': 'GoogleDrive',
            'n8n-nodes-base.dropbox': 'Dropbox',
            'n8n-nodes-base.jira': 'Jira',
            'n8n-nodes-base.github': 'GitHub',
            'n8n-nodes-base.gitlab': 'GitLab',
            'n8n-nodes-base.twitter': 'Twitter',
            'n8n-nodes-base.facebook': 'Facebook',
            'n8n-nodes-base.linkedin': 'LinkedIn',
            'n8n-nodes-base.zoom': 'Zoom',
            'n8n-nodes-base.calendly': 'Calendly',
            'n8n-nodes-base.typeform': 'Typeform',
            'n8n-nodes-base.mailchimp': 'Mailchimp',
            'n8n-nodes-base.sendgrid': 'SendGrid',
            'n8n-nodes-base.twilio': 'Twilio',
        }
        
        # Action keywords for purpose detection
        self.action_keywords = {
            'create': ['create', 'add', 'new', 'insert', 'generate'],
            'update': ['update', 'edit', 'modify', 'change', 'sync'],
            'delete': ['delete', 'remove', 'clean', 'purge'],
            'send': ['send', 'notify', 'alert', 'email', 'message'],
            'backup': ['backup', 'export', 'archive', 'save'],
            'monitor': ['monitor', 'check', 'watch', 'track'],
            'process': ['process', 'transform', 'convert', 'parse'],
            'import': ['import', 'fetch', 'get', 'retrieve', 'pull']
        }
    
    def analyze_workflow(self, file_path: str) -> Dict:
        """Analyze a workflow file and extract meaningful metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self.errors.append(f"Error reading {file_path}: {str(e)}")
            return None
        
        filename = os.path.basename(file_path)
        nodes = data.get('nodes', [])
        
        # Extract services and integrations
        services = self.extract_services(nodes)
        
        # Determine trigger type
        trigger_type = self.determine_trigger_type(nodes)
        
        # Extract purpose/action
        purpose = self.extract_purpose(data, nodes)
        
        # Get workflow name from JSON (might be better than filename)
        json_name = data.get('name', '').strip()
        
        return {
            'filename': filename,
            'json_name': json_name,
            'services': services,
            'trigger_type': trigger_type,
            'purpose': purpose,
            'node_count': len(nodes),
            'has_description': bool(data.get('meta', {}).get('description', '').strip())
        }
    
    def extract_services(self, nodes: List[Dict]) -> List[str]:
        """Extract unique services/integrations from workflow nodes."""
        services = set()
        
        for node in nodes:
            node_type = node.get('type', '')
            
            # Map known service types
            if node_type in self.service_mappings:
                services.add(self.service_mappings[node_type])
            elif node_type.startswith('n8n-nodes-base.'):
                # Extract service name from node type
                service = node_type.replace('n8n-nodes-base.', '')
                service = re.sub(r'Trigger$', '', service)  # Remove Trigger suffix
                service = service.title()
                
                # Skip generic nodes
                if service not in ['Set', 'Function', 'If', 'Switch', 'Merge', 'StickyNote', 'NoOp']:
                    services.add(service)
        
        return sorted(list(services))[:3]  # Limit to top 3 services
    
    def determine_trigger_type(self, nodes: List[Dict]) -> str:
        """Determine the primary trigger type of the workflow."""
        for node in nodes:
            node_type = node.get('type', '').lower()
            
            if 'webhook' in node_type:
                return 'Webhook'
            elif 'cron' in node_type or 'schedule' in node_type:
                return 'Scheduled'
            elif 'trigger' in node_type and 'manual' not in node_type:
                return 'Triggered'
        
        return 'Manual'
    
    def extract_purpose(self, data: Dict, nodes: List[Dict]) -> str:
        """Extract the main purpose/action of the workflow."""
        # Check workflow name first
        name = data.get('name', '').lower()
        
        # Check node names for action keywords
        node_names = [node.get('name', '').lower() for node in nodes]
        all_text = f"{name} {' '.join(node_names)}"
        
        # Find primary action
        for action, keywords in self.action_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                return action.title()
        
        # Fallback based on node types
        node_types = [node.get('type', '') for node in nodes]
        
        if any('email' in nt.lower() or 'gmail' in nt.lower() for nt in node_types):
            return 'Email'
        elif any('database' in nt.lower() or 'mysql' in nt.lower() for nt in node_types):
            return 'Database'
        elif any('api' in nt.lower() or 'http' in nt.lower() for nt in node_types):
            return 'API'
        
        return 'Automation'
    
    def generate_new_name(self, analysis: Dict, preserve_id: bool = True) -> str:
        """Generate a new, meaningful filename based on analysis."""
        filename = analysis['filename']
        
        # Extract existing ID if present
        id_match = re.match(r'^(\d+)_', filename)
        prefix = id_match.group(1) + '_' if id_match and preserve_id else ''
        
        # Use JSON name if it's meaningful and different from generic pattern
        json_name = analysis['json_name']
        if json_name and not re.match(r'^workflow_?\d*$', json_name.lower()):
            # Clean and use JSON name
            clean_name = self.clean_name(json_name)
            return f"{prefix}{clean_name}.json"
        
        # Build name from analysis
        parts = []
        
        # Add primary services
        if analysis['services']:
            parts.extend(analysis['services'][:2])  # Max 2 services
        
        # Add purpose
        if analysis['purpose']:
            parts.append(analysis['purpose'])
        
        # Add trigger type if not manual
        if analysis['trigger_type'] != 'Manual':
            parts.append(analysis['trigger_type'])
        
        # Fallback if no meaningful parts
        if not parts:
            parts = ['Custom', 'Workflow']
        
        new_name = '_'.join(parts)
        return f"{prefix}{new_name}.json"
    
    def clean_name(self, name: str) -> str:
        """Clean a name for use in filename."""
        # Replace problematic characters
        name = re.sub(r'[<>:"|?*]', '', name)
        name = re.sub(r'[^\w\s\-_.]', '_', name)
        name = re.sub(r'\s+', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        
        # Limit length
        if len(name) > 60:
            name = name[:60].rsplit('_', 1)[0]
        
        return name
    
    def identify_problematic_files(self) -> Dict[str, List[str]]:
        """Identify files that need renaming based on patterns."""
        if not os.path.exists(self.workflows_dir):
            print(f"Error: Directory '{self.workflows_dir}' not found.")
            return {}
        
        json_files = glob.glob(os.path.join(self.workflows_dir, "*.json"))
        
        patterns = {
            'generic_workflow': [],  # XXX_workflow_XXX.json
            'incomplete_names': [],  # Names ending with _
            'hash_only': [],         # Just hash without description
            'too_long': [],          # Names > 100 characters
            'special_chars': []      # Names with problematic characters
        }
        
        for file_path in json_files:
            filename = os.path.basename(file_path)
            
            # Generic workflow pattern
            if re.match(r'^\d+_workflow_\d+\.json$', filename):
                patterns['generic_workflow'].append(file_path)
            
            # Incomplete names
            elif filename.endswith('_.json') or filename.endswith('_'):
                patterns['incomplete_names'].append(file_path)
            
            # Hash-only names (8+ alphanumeric chars without descriptive text)
            elif re.match(r'^[a-zA-Z0-9]{8,}_?\.json$', filename):
                patterns['hash_only'].append(file_path)
            
            # Too long names
            elif len(filename) > 100:
                patterns['too_long'].append(file_path)
            
            # Special characters that might cause issues
            elif re.search(r'[<>:"|?*]', filename):
                patterns['special_chars'].append(file_path)
        
        return patterns
    
    def plan_renames(self, pattern_types: List[str] = None) -> List[Dict]:
        """Plan rename operations for specified pattern types."""
        if pattern_types is None:
            pattern_types = ['generic_workflow', 'incomplete_names']
        
        problematic = self.identify_problematic_files()
        rename_plan = []
        
        for pattern_type in pattern_types:
            files = problematic.get(pattern_type, [])
            print(f"\nProcessing {len(files)} files with pattern: {pattern_type}")
            
            for file_path in files:
                analysis = self.analyze_workflow(file_path)
                if analysis:
                    new_name = self.generate_new_name(analysis)
                    new_path = os.path.join(self.workflows_dir, new_name)
                    
                    # Avoid conflicts
                    counter = 1
                    while os.path.exists(new_path) and new_path != file_path:
                        name_part, ext = os.path.splitext(new_name)
                        new_name = f"{name_part}_{counter}{ext}"
                        new_path = os.path.join(self.workflows_dir, new_name)
                        counter += 1
                    
                    if new_path != file_path:  # Only rename if different
                        rename_plan.append({
                            'old_path': file_path,
                            'new_path': new_path,
                            'old_name': os.path.basename(file_path),
                            'new_name': new_name,
                            'pattern_type': pattern_type,
                            'analysis': analysis
                        })
        
        return rename_plan
    
    def execute_renames(self, rename_plan: List[Dict]) -> Dict:
        """Execute the rename operations."""
        results = {'success': 0, 'errors': 0, 'skipped': 0}
        
        for operation in rename_plan:
            old_path = operation['old_path']
            new_path = operation['new_path']
            
            try:
                if self.dry_run:
                    print(f"DRY RUN: Would rename:")
                    print(f"  {operation['old_name']} → {operation['new_name']}")
                    results['success'] += 1
                else:
                    os.rename(old_path, new_path)
                    print(f"Renamed: {operation['old_name']} → {operation['new_name']}")
                    results['success'] += 1
                    
            except Exception as e:
                print(f"Error renaming {operation['old_name']}: {str(e)}")
                results['errors'] += 1
        
        return results
    
    def generate_report(self, rename_plan: List[Dict]):
        """Generate a detailed report of planned renames."""
        print(f"\n{'='*80}")
        print(f"WORKFLOW RENAME REPORT")
        print(f"{'='*80}")
        print(f"Total files to rename: {len(rename_plan)}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}")
        
        # Group by pattern type
        by_pattern = {}
        for op in rename_plan:
            pattern = op['pattern_type']
            if pattern not in by_pattern:
                by_pattern[pattern] = []
            by_pattern[pattern].append(op)
        
        for pattern, operations in by_pattern.items():
            print(f"\n{pattern.upper()} ({len(operations)} files):")
            print("-" * 50)
            
            for op in operations[:10]:  # Show first 10 examples
                print(f"  {op['old_name']}")
                print(f"  → {op['new_name']}")
                print(f"    Services: {', '.join(op['analysis']['services']) if op['analysis']['services'] else 'None'}")
                print(f"    Purpose: {op['analysis']['purpose']}")
                print()
            
            if len(operations) > 10:
                print(f"  ... and {len(operations) - 10} more files")
                print()

def main():
    parser = argparse.ArgumentParser(description='Intelligent N8N Workflow Renamer')
    parser.add_argument('--dir', default='workflows', help='Workflows directory path')
    parser.add_argument('--execute', action='store_true', help='Execute renames (default is dry run)')
    parser.add_argument('--pattern', choices=['generic_workflow', 'incomplete_names', 'hash_only', 'too_long', 'all'], 
                       default='generic_workflow', help='Pattern type to process')
    parser.add_argument('--report-only', action='store_true', help='Generate report without renaming')
    
    args = parser.parse_args()
    
    # Determine patterns to process
    if args.pattern == 'all':
        patterns = ['generic_workflow', 'incomplete_names', 'hash_only', 'too_long']
    else:
        patterns = [args.pattern]
    
    # Initialize renamer
    renamer = WorkflowRenamer(
        workflows_dir=args.dir,
        dry_run=not args.execute
    )
    
    # Plan renames
    print("Analyzing workflows and planning renames...")
    rename_plan = renamer.plan_renames(patterns)
    
    # Generate report
    renamer.generate_report(rename_plan)
    
    if not args.report_only and rename_plan:
        print(f"\n{'='*80}")
        if args.execute:
            print("EXECUTING RENAMES...")
            results = renamer.execute_renames(rename_plan)
            print(f"\nResults: {results['success']} successful, {results['errors']} errors")
        else:
            print("DRY RUN COMPLETE")
            print("Use --execute flag to perform actual renames")
            print("Use --report-only to see analysis without renaming")

if __name__ == "__main__":
    main()