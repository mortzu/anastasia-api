import lxc
import socket
import pwd
import glob
import os
import subprocess
import json

class LXC:
    container_path = '/var/lib/lxc/'
    unprivileged_container_path = '/var/lib/vps/'
    cgroup_path = '/sys/fs/cgroup/'

    def __init__(self, libvirt_uri = None, enable_ssh_console = False):
        self.enable_ssh_console = enable_ssh_console

    def get_domains(self):
        # dictionary for result
        result = {}

        result['hostname'] = socket.getfqdn()
        result['hypervisor'] = 'LXC'

        for container in glob.glob(self.container_path + '*/config') + glob.glob(self.unprivileged_container_path + 'vps*/.local/share/lxc/*/config'):
            domain_name = os.path.basename(container.rstrip('/config'))
            result[domain_name] = {}
            result[domain_name]['id'] = 0
            result[domain_name]['vcpu'] = 0
            result[domain_name]['name'] = domain_name

            if self.unprivileged_container_path in container:
                lxc_username = os.path.basename(os.path.dirname(container.rstrip('/config')).rstrip('/.local/share/lxc'))

                try:
                    pwd.getpwnam(lxc_username)
                except:
                    continue

                proc = subprocess.Popen('/usr/bin/sudo -Hu ' + lxc_username + ' /opt/anastasia-api/lxc-info-json.py ' + domain_name, shell = True, stdout = subprocess.PIPE)
                data = json.loads(proc.communicate()[0])

                if self.enable_ssh_console:
                    result[domain_name]['console_type'] = 'SSH'
                    result[domain_name]['console_address'] = result['hostname']
                    result[domain_name]['console_port'] = 22
                    result[domain_name]['console_username'] = lxc_username

                result[domain_name]['unprivileged'] = True
                result[domain_name]['state'] = data['state']
                result[domain_name]['memory'] = data['memory']
                result[domain_name]['ip'] = data['ip']
            else:
                cont = lxc.Container(domain_name)

                result[domain_name]['unprivileged'] = False
                result[domain_name]['console_type'] = None
                result[domain_name]['console_address'] = None
                result[domain_name]['console_port'] = None
                result[domain_name]['console_username'] = None

                result[domain_name]['state'] = cont.state.swapcase()

                try:
                    result[domain_name]['memory'] = int(open(self.cgroup_path + 'memory/lxc/' + domain_name + '/memory.limit_in_bytes', 'r').read()) / 1024
                except:
                    result[domain_name]['memory'] = 0

                try:
                    result[domain_name]['swap'] = (int(open(self.cgroup_path + 'memory/lxc/' + domain_name + '/memory.memsw.limit_in_bytes', 'r').read()) / 1024) - result['memory']
                except:
                    result[domain_name]['swap'] = 0

                result[domain_name]['ip'] = cont.get_ips(timeout = 5)

        return result

    def domain_start(self, name):
        if not os.path.exists(self.container_path + name):
            return False
        cont = lxc.Container(name)
        return cont.start()

    def domain_shutdown(self, name):
        if not os.path.exists(self.container_path + name):
            return False
        cont = lxc.Container(name)
        return cont.shutdown()

    def domain_reboot(self, name):
        return False

    def domain_destroy(self, name):
        if not os.path.exists(self.container_path + name):
            return False
        cont = lxc.Container(name)
        return cont.stop()
