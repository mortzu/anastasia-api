import libvirt
import xml.etree.ElementTree as ET

class Libvirt:
    states = {
        libvirt.VIR_DOMAIN_NOSTATE: 'no state',
        libvirt.VIR_DOMAIN_RUNNING: 'running',
        libvirt.VIR_DOMAIN_BLOCKED: 'blocked on resource',
        libvirt.VIR_DOMAIN_PAUSED: 'paused by user',
        libvirt.VIR_DOMAIN_SHUTDOWN: 'being shut down',
        libvirt.VIR_DOMAIN_SHUTOFF: 'shut off',
        libvirt.VIR_DOMAIN_CRASHED: 'crashed',
    }

    def __init__(self, libvirt_uri = None):
        # connect to libvirt
        conn = libvirt.open(libvirt_uri)

    def get_domains(self):
        # dictionary for result
        result = {}

        # get hostname
        result['hostname'] = conn.getHostname()
        result['hypervisor'] = conn.getType()
        result['uri'] = conn.getURI()

        domlist = []

        for id in conn.listDomainsID():
            domlist.append(self.conn.lookupByID(id))

        for id in conn.listDefinedDomains():
            domlist.append(self.conn.lookupByName(id))

        for dom in domlist:
            infos = dom.info()
            domain_name = dom.name()
            xml_root = ET.fromstring(dom.XMLDesc())
            result[domain_name] = {}
            result[domain_name]['id'] = dom.ID()
            result[domain_name]['state'] = self.states.get(dom.state()[0], dom.state()[0])
            result[domain_name]['name'] = dom.name()
            result[domain_name]['memory'] = dom.maxMemory()

            if dom.state()[0] == 1:
                result[domain_name]['vcpu'] = dom.maxVcpus()
            else:
                result[domain_name]['vcpu'] = 0

            result[domain_name]['vnc_address'] = xml_root.find('./devices/graphics').get('listen')
            result[domain_name]['vnc_port'] = xml_root.find('./devices/graphics').get('port')

        return result

    def domain_start(self, name):
        # get domain
        dom = self.conn.lookupByName(name)
        dom.create()

    def domain_shutdown(self, name):
        # get domain
        dom = self.conn.lookupByName(name)
        dom.shutdown()

    def domain_reboot(self, name):
        return False

    def domain_destroy(self, name):
        # get domain
        dom = self.conn.lookupByName(name)
        dom.destroy()
