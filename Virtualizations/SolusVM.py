import solusvm

class SolusVM:
    conn = None

    def __init__(self, cli_args = None):
        # Create SolusVM API
        self.conn = solusvm.SolusVM(url = cli_args.solusvm_url, api_id = cli_args.solusvm_id, api_key = cli_args.solusvm_key)

    def get_domains(self):
        # dictionary for result
        result = {}

        account = self.manager.get_account()

        droplets = self.manager.get_all_droplets()
        for droplet in droplets:
            domain_name = droplet.name
            result[domain_name] = {}
            result[domain_name]['id'] = droplet.id
            result[domain_name]['state'] = True if droplet.status == 'active' else False
            result[domain_name]['name'] = droplet.name
            result[domain_name]['memory'] = droplet.memory * 1024
            result[domain_name]['vcpu'] = droplet.vcpus
            result[domain_name]['ip_assignment'] = [droplet.ip_address]
            result[domain_name]['hostname'] = 'solusvm.com'
            result[domain_name]['hypervisor'] = 'SolusVM'
            result[domain_name]['uri'] = 'http://solusvm.com/'

        return result

    def domain_start(self, name):
        return 501

    def domain_stop(self, name):
        return 501

    def domain_shutdown(self, name):
        return 501

    def domain_restart(self, name):
        return 501

    def domain_reboot(self, name):
        return 501
