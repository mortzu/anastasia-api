import lxc
import socket
import pwd
import glob
import os

class LXC:
    container_path = "/var/lib/lxc/"
    cgroup_path = "/sys/fs/cgroup/"

    def __init__(self, libvirt_uri = None, enable_ssh_console = False):
        self.enable_ssh_console = enable_ssh_console

    def pages2mb(self, pages):
        return pages * 4096 / 1024 / 1024

    def get_domains(self):
        # dictionary for result
        result = {}

        result['hostname'] = socket.getfqdn()
        result['hypervisor'] = 'LXC'

        for container in glob.glob(self.container_path + '*/config'):
            domain_name = container.replace(self.container_path, "").rstrip("/config")
            result[domain_name] = {}

            cont = lxc.Container(domain_name)

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

            result[domain_name]['id'] = 0
            result[domain_name]['state'] = cont.state.swapcase()
            result[domain_name]['name'] = domain_name

            try:
                result[domain_name]['memory'] = int(open(self.cgroup_path + "memory/lxc/" + domain_name + "/memory.limit_in_bytes", 'r').read()) / 1024
            except:
                result[domain_name]['memory'] = 0
            result[domain_name]['vcpu'] = 0
            result[domain_name]['ip'] = cont.get_ips(timeout=5)

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
