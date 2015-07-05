import subprocess
import socket
import json
import pwd

class OpenVZ:
    def __init__(self, libvirt_uri = None, enable_ssh_console = False):
        self.enable_ssh_console = enable_ssh_console

    def shellquote(self, s):
        return "'" + s.replace("'", "'\\''") + "'"

    def pages2mb(self, pages):
        return pages * 4096 / 1024 / 1024

    def get_domains(self):
        # dictionary for result
        result = {}

        proc = subprocess.Popen('vzlist --json -a', shell = True, stdout = subprocess.PIPE)
        data = json.loads(proc.communicate()[0])

        result['hostname'] = socket.getfqdn()
        result['hypervisor'] = 'OpenVZ'

        for ct in data:
            domain_name = ct['hostname']
            result[domain_name] = {}

            if self.enable_ssh_console:
                try:
                    pwd.getpwnam('vps' + str(ct['ctid']))
                    result[domain_name]['console_type'] = 'SSH'
                    result[domain_name]['console_address'] = result['hostname']
                    result[domain_name]['console_port'] = 22
                except KeyError:
                    result[domain_name]['console_type'] = None
                    result[domain_name]['console_address'] = None
                    result[domain_name]['console_port'] = None

            result[domain_name]['id'] = ct['ctid']
            result[domain_name]['state'] = ct['status']
            result[domain_name]['name'] = domain_name
            result[domain_name]['memory'] = self.pages2mb(ct['physpages']['limit']) * 1024
            result[domain_name]['vcpu'] = ct['cpus']
            result[domain_name]['ip'] = ct['ip']

        return result

    def domain_start(self, name):
        proc = subprocess.Popen('vzctl start ' + self.shellquote(name), shell=True, stdout=subprocess.PIPE)

    def domain_shutdown(self, name):
        proc = subprocess.Popen('vzctl stop ' + self.shellquote(name), shell=True, stdout=subprocess.PIPE)

    def domain_reboot(self, name):
        proc = subprocess.Popen('vzctl restart ' + self.shellquote(name), shell=True, stdout=subprocess.PIPE)
