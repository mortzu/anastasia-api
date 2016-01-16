from scaleway.apis import ComputeAPI

class Scaleway:
    conn = None

    def __init__(self, cli_args = None):
        # Create Scaleway API
        self.conn = ComputeAPI(auth_token = cli_args.scaleway_key)

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
                result[domain_name]['ip_assignment'] = [server['public_ip']['address'], server['private_ip']]

        return result

    def domain_start(self, name):
        return 501

    def domain_shutdown(self, name):
        return 501

    def domain_reboot(self, name):
        return 501

    def domain_stop(self, name):
        return 501
