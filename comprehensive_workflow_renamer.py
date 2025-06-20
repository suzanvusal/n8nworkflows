#!/usr/bin/env python3
"""
Comprehensive N8N Workflow Renamer
Complete standardization of all 2053+ workflows with uniform naming convention.
"""

import json
import os
import glob
import re
import shutil
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

class ComprehensiveWorkflowRenamer:
    """Renames ALL workflows to uniform 0001-9999 standard with intelligent analysis."""
    
    def __init__(self, workflows_dir: str = "workflows"):
        self.workflows_dir = workflows_dir
        self.rename_log = []
        self.errors = []
        self.backup_dir = "workflow_backups"
        
    def analyze_all_workflows(self) -> Dict[str, Any]:
        """Analyze all workflow files and generate comprehensive rename plan."""
        if not os.path.exists(self.workflows_dir):
            print(f"❌ Workflows directory '{self.workflows_dir}' not found.")
            return {'workflows': [], 'total': 0, 'errors': []}
        
        json_files = glob.glob(os.path.join(self.workflows_dir, "*.json"))
        
        if not json_files:
            print(f"❌ No JSON files found in '{self.workflows_dir}' directory.")
            return {'workflows': [], 'total': 0, 'errors': []}
        
        print(f"🔍 Analyzing {len(json_files)} workflow files...")
        
        workflows = []
        for file_path in json_files:
            try:
                workflow_data = self._analyze_workflow_file(file_path)
                if workflow_data:
                    workflows.append(workflow_data)
            except Exception as e:
                error_msg = f"Error analyzing {file_path}: {str(e)}"
                print(f"❌ {error_msg}")
                self.errors.append(error_msg)
                continue
        
        # Sort by current filename for consistent numbering
        workflows.sort(key=lambda x: x['current_filename'])
        
        # Assign new sequential numbers
        for i, workflow in enumerate(workflows, 1):
            workflow['new_number'] = f"{i:04d}"
            workflow['new_filename'] = self._generate_new_filename(workflow, i)
        
        return {
            'workflows': workflows,
            'total': len(workflows),
            'errors': self.errors
        }
    
    def _analyze_workflow_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a single workflow file and extract metadata for renaming."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"❌ Error reading {file_path}: {str(e)}")
            return None
        
        filename = os.path.basename(file_path)
        
        # Extract workflow metadata
        workflow = {
            'current_filename': filename,
            'current_path': file_path,
            'name': data.get('name', filename.replace('.json', '')),
            'workflow_id': data.get('id', ''),
            'active': data.get('active', False),
            'nodes': data.get('nodes', []),
            'connections': data.get('connections', {}),
            'tags': data.get('tags', []),
            'created_at': data.get('createdAt', ''),
            'updated_at': data.get('updatedAt', '')
        }
        
        # Analyze nodes for intelligent naming
        node_count = len(workflow['nodes'])
        workflow['node_count'] = node_count
        
        # Determine complexity
        if node_count <= 5:
            complexity = 'Simple'
        elif node_count <= 15:
            complexity = 'Standard'
        else:
            complexity = 'Complex'
        workflow['complexity'] = complexity
        
        # Find services and trigger type
        services, trigger_type = self._analyze_nodes(workflow['nodes'])
        workflow['services'] = list(services)
        workflow['trigger_type'] = trigger_type
        
        # Determine purpose from name and nodes
        workflow['purpose'] = self._determine_purpose(workflow['name'], workflow['nodes'])
        
        return workflow
    
    def _analyze_nodes(self, nodes: List[Dict]) -> Tuple[set, str]:
        """Analyze nodes to determine services and trigger type."""
        services = set()
        trigger_type = 'Manual'
        
        for node in nodes:
            node_type = node.get('type', '')
            node_name = node.get('name', '')
            
            # Determine trigger type
            if any(x in node_type.lower() for x in ['webhook', 'http']):
                trigger_type = 'Webhook'
            elif any(x in node_type.lower() for x in ['cron', 'schedule', 'interval']):
                trigger_type = 'Scheduled'
            elif 'trigger' in node_type.lower() and trigger_type == 'Manual':
                trigger_type = 'Triggered'
            
            # Extract service names
            if node_type.startswith('n8n-nodes-base.'):
                service = node_type.replace('n8n-nodes-base.', '')
                service = service.replace('Trigger', '').replace('trigger', '')
                
                # Clean up service names
                service_mapping = {
                    'webhook': 'Webhook',
                    'httpRequest': 'HTTP',
                    'cron': 'Cron',
                    'gmail': 'Gmail',
                    'slack': 'Slack',
                    'googleSheets': 'GoogleSheets',
                    'airtable': 'Airtable',
                    'notion': 'Notion',
                    'telegram': 'Telegram',
                    'discord': 'Discord',
                    'twitter': 'Twitter',
                    'github': 'GitHub',
                    'hubspot': 'HubSpot',
                    'salesforce': 'Salesforce',
                    'stripe': 'Stripe',
                    'shopify': 'Shopify',
                    'trello': 'Trello',
                    'asana': 'Asana',
                    'clickup': 'ClickUp',
                    'calendly': 'Calendly',
                    'zoom': 'Zoom',
                    'mattermost': 'Mattermost',
                    'microsoftTeams': 'Teams',
                    'googleCalendar': 'GoogleCalendar',
                    'googleDrive': 'GoogleDrive',
                    'dropbox': 'Dropbox',
                    'onedrive': 'OneDrive',
                    'aws': 'AWS',
                    'azure': 'Azure',
                    'googleCloud': 'GCP'
                }
                
                clean_service = service_mapping.get(service, service.title())
                
                # Skip utility nodes
                if clean_service not in ['Set', 'Function', 'If', 'Switch', 'Merge', 'StickyNote', 'NoOp']:
                    services.add(clean_service)
        
        return services, trigger_type
    
    def _determine_purpose(self, name: str, nodes: List[Dict]) -> str:
        """Determine workflow purpose from name and node analysis."""
        name_lower = name.lower()
        
        # Purpose keywords mapping
        purpose_keywords = {
            'create': ['create', 'add', 'new', 'generate', 'build'],
            'update': ['update', 'modify', 'change', 'edit', 'patch'],
            'sync': ['sync', 'synchronize', 'mirror', 'replicate'],
            'send': ['send', 'email', 'message', 'notify', 'alert'],
            'import': ['import', 'load', 'fetch', 'get', 'retrieve'],
            'export': ['export', 'save', 'backup', 'archive'],
            'monitor': ['monitor', 'check', 'watch', 'track', 'status'],
            'process': ['process', 'transform', 'convert', 'parse'],
            'automate': ['automate', 'workflow', 'bot', 'automation']
        }
        
        for purpose, keywords in purpose_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                return purpose.title()
        
        # Default purpose based on node analysis
        return 'Automation'
    
    def _generate_new_filename(self, workflow: Dict, number: int) -> str:
        """Generate new standardized filename."""
        # Format: 0001_Service1_Service2_Purpose_Trigger.json
        
        services = workflow['services'][:2]  # Max 2 services in filename
        purpose = workflow['purpose']
        trigger = workflow['trigger_type']
        
        # Build filename components
        parts = [f"{number:04d}"]
        
        # Add services
        if services:
            parts.extend(services)
        
        # Add purpose
        parts.append(purpose)
        
        # Add trigger if not Manual
        if trigger != 'Manual':
            parts.append(trigger)
        
        # Join and clean filename
        filename = '_'.join(parts)
        filename = re.sub(r'[^\w\-_]', '', filename)  # Remove special chars
        filename = re.sub(r'_+', '_', filename)  # Collapse multiple underscores
        filename = filename.strip('_')  # Remove leading/trailing underscores
        
        return f"{filename}.json"
    
    def create_backup(self) -> bool:
        """Create backup of current workflows directory."""
        try:
            if os.path.exists(self.backup_dir):
                shutil.rmtree(self.backup_dir)
            
            shutil.copytree(self.workflows_dir, self.backup_dir)
            print(f"✅ Backup created at: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    
    def execute_rename_plan(self, rename_plan: Dict[str, Any], dry_run: bool = True) -> bool:
        """Execute the comprehensive rename plan."""
        if not rename_plan['workflows']:
            print("❌ No workflows to rename.")
            return False
        
        print(f"\n{'🔍 DRY RUN - ' if dry_run else '🚀 EXECUTING - '}Renaming {rename_plan['total']} workflows")
        
        if not dry_run:
            if not self.create_backup():
                print("❌ Cannot proceed without backup.")
                return False
        
        success_count = 0
        
        for workflow in rename_plan['workflows']:
            old_path = workflow['current_path']
            new_filename = workflow['new_filename']
            new_path = os.path.join(self.workflows_dir, new_filename)
            
            # Check for filename conflicts
            if os.path.exists(new_path) and old_path != new_path:
                print(f"⚠️  Conflict: {new_filename} already exists")
                continue
            
            if dry_run:
                print(f"📝 {workflow['current_filename']} → {new_filename}")
            else:
                try:
                    os.rename(old_path, new_path)
                    self.rename_log.append({
                        'old': workflow['current_filename'],
                        'new': new_filename,
                        'services': workflow['services'],
                        'purpose': workflow['purpose'],
                        'trigger': workflow['trigger_type']
                    })
                    success_count += 1
                    print(f"✅ {workflow['current_filename']} → {new_filename}")
                except Exception as e:
                    error_msg = f"❌ Failed to rename {workflow['current_filename']}: {e}"
                    print(error_msg)
                    self.errors.append(error_msg)
        
        if not dry_run:
            print(f"\n🎉 Rename complete: {success_count}/{rename_plan['total']} workflows renamed")
            self._save_rename_log()
        
        return True
    
    def _save_rename_log(self):
        """Save detailed rename log to file."""
        log_data = {
            'timestamp': os.popen('date').read().strip(),
            'total_renamed': len(self.rename_log),
            'errors': self.errors,
            'renames': self.rename_log
        }
        
        with open('workflow_rename_log.json', 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Rename log saved to: workflow_rename_log.json")
    
    def generate_report(self, rename_plan: Dict[str, Any]) -> str:
        """Generate comprehensive rename report."""
        workflows = rename_plan['workflows']
        total = rename_plan['total']
        
        # Statistics
        services_count = {}
        purposes_count = {}
        triggers_count = {}
        
        for workflow in workflows:
            for service in workflow['services']:
                services_count[service] = services_count.get(service, 0) + 1
            
            purposes_count[workflow['purpose']] = purposes_count.get(workflow['purpose'], 0) + 1
            triggers_count[workflow['trigger_type']] = triggers_count.get(workflow['trigger_type'], 0) + 1
        
        report = f"""
# 🎯 Comprehensive Workflow Rename Plan

## 📊 Overview
- **Total workflows**: {total}
- **Naming convention**: 0001-{total:04d}_Service1_Service2_Purpose_Trigger.json
- **Quality improvement**: 100% standardized naming

## 🏷️ Service Distribution
"""
        
        for service, count in sorted(services_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"- **{service}**: {count} workflows\n"
        
        report += f"\n## 🎯 Purpose Distribution\n"
        for purpose, count in sorted(purposes_count.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{purpose}**: {count} workflows\n"
        
        report += f"\n## ⚡ Trigger Distribution\n"
        for trigger, count in sorted(triggers_count.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{trigger}**: {count} workflows\n"
        
        report += f"""
## 📝 Naming Examples
"""
        
        for i, workflow in enumerate(workflows[:10]):
            report += f"- `{workflow['current_filename']}` → `{workflow['new_filename']}`\n"
        
        if len(workflows) > 10:
            report += f"... and {len(workflows) - 10} more workflows\n"
        
        return report


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive N8N Workflow Renamer')
    parser.add_argument('--analyze', action='store_true', help='Analyze all workflows and create rename plan')
    parser.add_argument('--execute', action='store_true', help='Execute the rename plan (requires --analyze first)')
    parser.add_argument('--dry-run', action='store_true', help='Show rename plan without executing')
    parser.add_argument('--report', action='store_true', help='Generate comprehensive report')
    
    args = parser.parse_args()
    
    renamer = ComprehensiveWorkflowRenamer()
    
    if args.analyze or args.dry_run or args.report:
        print("🔍 Analyzing all workflows...")
        rename_plan = renamer.analyze_all_workflows()
        
        if args.report:
            report = renamer.generate_report(rename_plan)
            print(report)
        
        if args.dry_run:
            renamer.execute_rename_plan(rename_plan, dry_run=True)
        
        if args.execute:
            confirm = input(f"\n⚠️  This will rename {rename_plan['total']} workflows. Continue? (yes/no): ")
            if confirm.lower() == 'yes':
                renamer.execute_rename_plan(rename_plan, dry_run=False)
            else:
                print("❌ Rename cancelled.")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()