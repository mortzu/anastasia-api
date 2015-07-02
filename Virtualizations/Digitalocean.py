import digitalocean

class Digitalocean:
    manager = None

    def __init__(self, token = None, enable_ssh_console = False):
        # connect to digitalocean
        self.manager = digitalocean.Manager(token = token)

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
            result[domain_name]['state'] = droplet.status
            result[domain_name]['name'] = droplet.name
            result[domain_name]['memory'] = droplet.memory
            result[domain_name]['vcpu'] = droplet.vcpus
            result[domain_name]['ip'] = droplet.ip_address

        return result

    def domain_start(self, name):
        return False

    def domain_shutdown(self, name):
        return False

    def domain_reboot(self, name):
        return False

    def domain_destroy(self, name):
        return False