from scaleway.apis import ComputeAPI

class Scaleway:
    conn = None

    def __init__(self, api_key, enable_ssh_console = False):
        # Create Scaleway API
        self.conn = ComputeAPI(auth_token = api_key)

    def get_domains(self):
        # dictionary for result
        result = {}

        servers = self.conn.query().servers.get()

        # get hostname
        result['hostname'] = ''
        result['hypervisor'] = 'Scaleway'
        result['uri'] = 'https://www.scaleway.com'

        for key, value in servers.iteritems():
            for server in value:
                domain_name = str(server['name'])
                result[domain_name] = {}
                result[domain_name]['id'] = str(server['id'])
                result[domain_name]['state'] = True if server['state'] == 'running' else False
                result[domain_name]['name'] = domain_name
                result[domain_name]['memory'] = 2097152 if str(server['commercial_type']) == 'C1' else 0
                result[domain_name]['vcpu'] = 2 if str(server['commercial_type']) == 'C1' else 0
                result[domain_name]['ip'] = [server['public_ip']['address'], server['private_ip']]

        return result

    def domain_start(self, name):
        return False

    def domain_shutdown(self, name):
        return False

    def domain_reboot(self, name):
        return False

    def domain_destroy(self, name):
        return False
