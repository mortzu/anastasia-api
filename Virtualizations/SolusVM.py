import solusvm

class SolusVM:
    conn = None

    def __init__(self, url, api_id, api_key, enable_ssh_console = False):
        # Create SolusVM API
        self.conn = solusvm.SolusVM(url = url, api_id = api_id, api_key = api_key)

    def get_domains(self):
        # dictionary for result
        result = {}

        account = self.manager.get_account()

        # get hostname
        result['hostname'] = account.uuid
        result['hypervisor'] = 'Digitalocean'
        result['uri'] = 'https://www.digitalocean.com'

        droplets = self.manager.get_all_droplets()
        for droplet in droplets:
            domain_name = droplet.name
            result[domain_name] = {}
            result[domain_name]['id'] = droplet.id
            result[domain_name]['state'] = True if droplet.status == 'active' else False
            result[domain_name]['name'] = droplet.name
            result[domain_name]['memory'] = droplet.memory * 1024
            result[domain_name]['vcpu'] = droplet.vcpus
            result[domain_name]['ip'] = [droplet.ip_address]

        return result

    def domain_start(self, name):
        return False

    def domain_shutdown(self, name):
        return False

    def domain_reboot(self, name):
        return False

    def domain_destroy(self, name):
        return False