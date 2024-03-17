#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from parser.inventory import InventoryParser
from parser.facts import FactsParser

def process_inventory_files(inventory_dir):
    inventory_parser = InventoryParser()
    for root, _, files in os.walk(inventory_dir):
        for file in files:
            if file.endswith('.yml'):
                filepath = os.path.join(root, file)
                inventory_parser.parse_file(filepath)
    return inventory_parser

def process_facts_files(facts_dir):
    facts_parser = FactsParser()
    for item in os.listdir(facts_dir):
        filepath = os.path.join(facts_dir, item)
        if os.path.isfile(filepath):
            facts_parser.parse_file(filepath)
    return facts_parser

def format_host_data(hostname, host_info, facts):
    host_facts = facts.get_host_facts(hostname)
    memory_info = facts.get_memory_info(hostname)
    processor_info = facts.get_processor_info(hostname)
    disk_info = facts.get_disk_info(hostname)
    network_info = facts.get_network_info(hostname)
    
    return {
        'hostname': hostname,
        'os': host_facts.get('ansible_distribution', 'Unknown'),
        'os_version': host_facts.get('ansible_distribution_version', ''),
        'kernel': host_facts.get('ansible_kernel', 'Unknown'),
        'architecture': host_facts.get('ansible_architecture', 'Unknown'),
        'memory': round(memory_info['total'] / 1024, 1),  # Convert to GB
        'cpu_cores': processor_info['cores'],
        'groups': host_info['groups'],
        'ip_address': network_info['ipv4'],
        'network': host_facts.get('ansible_default_ipv4', {}).get('network', 'Unknown'),
        'gateway': host_facts.get('ansible_default_ipv4', {}).get('gateway', 'Unknown'),
        'mounts': [
            {
                'device': mount.get('device', ''),
                'mount': mount.get('mount', ''),
                'fstype': mount.get('fstype', ''),
                'size_total': mount.get('size_total', 0),
                'size_available': mount.get('size_available', 0)
            }
            for mount in host_facts.get('ansible_mounts', [])
        ]
    }

def generate_dashboard(inventory_dir, facts_dir, output_file):
    print("\nProcessing inventory files...")
    inventory_parser = process_inventory_files(inventory_dir)
    
    print("\nProcessing facts files...")
    facts_parser = process_facts_files(facts_dir)
    
    # Prepare data for the template
    hosts_data = []
    operating_systems = set()
    
    for hostname, host_info in inventory_parser.hosts.items():
        host_data = format_host_data(hostname, host_info, facts_parser)
        hosts_data.append(host_data)
        operating_systems.add(host_data['os'])
    
    # Sort hosts by hostname
    hosts_data.sort(key=lambda x: x['hostname'])
    
    # Get unique groups
    groups = sorted(list(set(
        group
        for host in inventory_parser.hosts.values()
        for group in host['groups']
    )))
    
    # Get unique operating systems
    operating_systems = sorted(list(operating_systems))
    
    print("\nGenerating dashboard...")
    
    # Load and render template
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('static_dashboard.html')
    
    dashboard_html = template.render(
        hosts=hosts_data,
        groups=groups,
        operating_systems=operating_systems,
        generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # Write output file
    with open(output_file, 'w') as f:
        f.write(dashboard_html)
    
    print(f"\nDashboard generated successfully: {output_file}")
    print(f"Total hosts processed: {len(hosts_data)}")
    print(f"Total groups processed: {len(groups)}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python generate_dashboard.py <inventory_dir> <facts_dir> <output_file>")
        sys.exit(1)
    
    inventory_dir = sys.argv[1]
    facts_dir = sys.argv[2]
    output_file = sys.argv[3]
    
    generate_dashboard(inventory_dir, facts_dir, output_file)
