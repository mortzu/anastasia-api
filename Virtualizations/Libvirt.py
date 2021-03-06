import libvirt
import xml.etree.ElementTree as ET

class Libvirt:
    conn = None
    debian_version = 8

    states = {
        libvirt.VIR_DOMAIN_NOSTATE: 'no state',
        libvirt.VIR_DOMAIN_RUNNING: 'running',
        libvirt.VIR_DOMAIN_BLOCKED: 'blocked on resource',
        libvirt.VIR_DOMAIN_PAUSED: 'paused by user',
        libvirt.VIR_DOMAIN_SHUTDOWN: 'being shut down',
        libvirt.VIR_DOMAIN_SHUTOFF: 'shut off',
        libvirt.VIR_DOMAIN_CRASHED: 'crashed',
    }

    def __init__(self, cli_args = None):
        # Get debian version
        try:
            self.debian_version = int(open('/etc/debian_version', 'r').read().split('.')[0])
        except:
            pass

        # Connect to libvirt
        self.conn = libvirt.open(cli_args.libvirt_uri)

    def get_domains(self):
        # Dictionary for result
        result = {}

        domlist = []

        for id in self.conn.listDomainsID():
            domlist.append(self.conn.lookupByID(id))

        for id in self.conn.listDefinedDomains():
            domlist.append(self.conn.lookupByName(id))

        for dom in domlist:
            infos = dom.info()
            domain_name = dom.name()

            if self.debian_version < 8:
                xml_root = ET.fromstring(dom.XMLDesc(0))
            else:
                xml_root = ET.fromstring(dom.XMLDesc())

            result[domain_name] = {}
            result[domain_name]['id'] = dom.ID()

            if self.debian_version < 8:
                result[domain_name]['state'] = self.states.get(dom.state(0)[0], dom.state(0)[0])
            else:
                result[domain_name]['state'] = self.states.get(dom.state()[0], dom.state()[0])

            result[domain_name]['name'] = dom.name()
            result[domain_name]['memory'] = dom.maxMemory()

            if result[domain_name]['state'] == 'running':
                result[domain_name]['vcpu'] = dom.maxVcpus()
            else:
                result[domain_name]['vcpu'] = 0

            try:
                result[domain_name]['console_type'] = 'VNC'
                result[domain_name]['console_address'] = xml_root.find('./devices/graphics').get('listen')
                result[domain_name]['console_port'] = xml_root.find('./devices/graphics').get('port')
            except:
                pass

            result[domain_name]['hostname'] = self.conn.getHostname()
            result[domain_name]['hypervisor'] = self.conn.getType()
            result[domain_name]['uri'] = self.conn.getURI()

        return result

    def domain_start(self, name):
        try:
            dom = self.conn.lookupByName(name)
        except:
            return 404

        try:
            dom.create()
        except:
            return 500

        return 200

    def domain_stop(self, name):
        try:
            dom = self.conn.lookupByName(name)
        except:
            return 404

        try:
            dom.destroy()
        except:
            return 500

        return 200

    def domain_shutdown(self, name):
        try:
            dom = self.conn.lookupByName(name)
        except:
            return 404

        try:
            dom.shutdown()
        except:
            return 500

        return 200

    def domain_restart(self, name):
        try:
            dom = self.conn.lookupByName(name)
        except:
            return 404

        try:
            dom.reset()
        except:
            return 500

        return 200

    def domain_reboot(self, name):
        try:
            dom = self.conn.lookupByName(name)
        except:
            return 404

        try:
            dom.reboot()
        except:
            return 500

        return 200
