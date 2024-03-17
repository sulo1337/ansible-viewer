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
                
            if not inventory:
                return False

            # Process all top-level groups including 'all'
            for group_name, group_data in inventory.items():
                self._process_group(group_name, group_data)
                
            return True
            
        except Exception as e:
            print(f"Error parsing inventory file {filepath}: {str(e)}")
            return False

    def _process_group(self, group_name, group_data):
        # Initialize group if not exists
        if group_name not in self.groups:
            self.groups[group_name] = {
                'hosts': [],
                'vars': {},
                'children': []
            }

        # Process group vars
        if 'vars' in group_data:
            self.groups[group_name]['vars'].update(group_data['vars'])

        # Process direct hosts in group
        if 'hosts' in group_data:
            for hostname, host_vars in group_data['hosts'].items():
                self.groups[group_name]['hosts'].append(hostname)
                if hostname not in self.hosts:
                    self.hosts[hostname] = {
                        'groups': [group_name],
                        'vars': {}
                    }
                else:
                    if group_name not in self.hosts[hostname]['groups']:
                        self.hosts[hostname]['groups'].append(group_name)
                if host_vars:
                    self.hosts[hostname]['vars'].update(host_vars)

        # Process children groups recursively
        if 'children' in group_data:
            for child_name, child_data in group_data['children'].items():
                self.groups[group_name]['children'].append(child_name)
                self._process_group(child_name, child_data)
                # Add hosts from child groups to parent group's host list
                if child_name in self.groups:
                    for hostname in self.groups[child_name]['hosts']:
                        if hostname not in self.groups[group_name]['hosts']:
                            self.groups[group_name]['hosts'].append(hostname)
                        if hostname in self.hosts and group_name not in self.hosts[hostname]['groups']:
                            self.hosts[hostname]['groups'].append(group_name)
            
    def get_host_groups(self, hostname):
        if hostname in self.hosts:
            return self.hosts[hostname]['groups']
        return []
        
    def get_group_hosts(self, group_name):
        if group_name in self.groups:
            return self.groups[group_name]['hosts']
        return []
