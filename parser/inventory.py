import yaml
import os

class InventoryParser:
    def __init__(self):
        self.hosts = {}
        self.groups = {}
        
    def parse_file(self, filepath):
        if not os.path.exists(filepath):
            return False
            
        try:
            with open(filepath, 'r') as f:
                inventory = yaml.safe_load(f)
                
            if not inventory or 'all' not in inventory:
                return False
                
            # Process hosts in 'all' group
            if 'hosts' in inventory['all']:
                for hostname, host_vars in inventory['all']['hosts'].items():
                    if hostname not in self.hosts:
                        self.hosts[hostname] = {
                            'groups': ['all'],
                            'vars': {}
                        }
                    if host_vars:
                        self.hosts[hostname]['vars'].update(host_vars)
            
            # Process children groups
            if 'children' in inventory['all']:
                for group_name, group_data in inventory['all']['children'].items():
                    if group_name not in self.groups:
                        self.groups[group_name] = {
                            'hosts': [],
                            'vars': {},
                            'children': []
                        }
                    
                    if 'hosts' in group_data:
                        for hostname in group_data['hosts'].keys():
                            self.groups[group_name]['hosts'].append(hostname)
                            if hostname not in self.hosts:
                                self.hosts[hostname] = {
                                    'groups': ['all', group_name],
                                    'vars': {}
                                }
                            else:
                                self.hosts[hostname]['groups'].append(group_name)
                    
                    if 'vars' in group_data:
                        self.groups[group_name]['vars'].update(group_data['vars'])
            
            return True
            
        except Exception as e:
            print(f"Error parsing inventory file {filepath}: {str(e)}")
            return False
            
    def get_host_groups(self, hostname):
        if hostname in self.hosts:
            return self.hosts[hostname]['groups']
        return []
        
    def get_group_hosts(self, group_name):
        if group_name in self.groups:
            return self.groups[group_name]['hosts']
        return []
