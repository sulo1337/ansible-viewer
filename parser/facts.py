import json
import os

class FactsParser:
    def __init__(self):
        self.facts = {}
        
    def parse_file(self, filepath):
        if not os.path.exists(filepath):
            return False
            
        try:
            with open(filepath, 'r') as f:
                facts = json.load(f)
                
            if not facts:
                return False
                
            # Each facts file contains facts for a single host
            hostname = os.path.basename(filepath)
            self.facts[hostname] = facts
            return True
            
        except Exception as e:
            print(f"Error parsing facts file {filepath}: {str(e)}")
            return False
            
    def get_host_facts(self, hostname):
        return self.facts.get(hostname, {})
        
    def get_all_facts(self):
        return self.facts
        
    def get_os_distribution(self, hostname):
        facts = self.get_host_facts(hostname)
        return facts.get('ansible_distribution', 'Unknown')
        
    def get_os_version(self, hostname):
        facts = self.get_host_facts(hostname)
        return facts.get('ansible_distribution_version', 'Unknown')
        
    def get_memory_info(self, hostname):
        facts = self.get_host_facts(hostname)
        return {
            'total': facts.get('ansible_memtotal_mb', 0),
            'free': facts.get('ansible_memfree_mb', 0)
        }
        
    def get_processor_info(self, hostname):
        facts = self.get_host_facts(hostname)
        return {
            'cores': facts.get('ansible_processor_cores', 0),
            'count': facts.get('ansible_processor_count', 0),
            'vcpus': facts.get('ansible_processor_vcpus', 0)
        }
        
    def get_disk_info(self, hostname):
        facts = self.get_host_facts(hostname)
        mounts = facts.get('ansible_mounts', [])
        total_size = 0
        total_available = 0
        for mount in mounts:
            if 'block_total' in mount and 'block_size' in mount:
                total_size += mount['block_total'] * mount['block_size']
            if 'block_available' in mount and 'block_size' in mount:
                total_available += mount['block_available'] * mount['block_size']
        return {
            'total_bytes': total_size,
            'available_bytes': total_available
        }
        
    def get_network_info(self, hostname):
        facts = self.get_host_facts(hostname)
        default_ipv4 = facts.get('ansible_default_ipv4', {})
        default_ipv6 = facts.get('ansible_default_ipv6', {})
        return {
            'ipv4': default_ipv4.get('address', ''),
            'ipv6': default_ipv6.get('address', ''),
            'interfaces': [k for k in facts.keys() if k.startswith('ansible_') and not k.startswith('ansible_local')]
        }
