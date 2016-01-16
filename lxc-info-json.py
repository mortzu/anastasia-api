#! /usr/bin/env python2

import sys
import lxc
import json
import os
import getpass

cgroup_path = '/sys/fs/cgroup/'
unprivileged = False

try:
    domain_name = sys.argv[1]
except:
    print 'Argument not given'
    sys.exit(1)

if os.getuid != 0:
    unprivileged = True

cont = lxc.Container(sys.argv[1])

result = {}
result['state'] = cont.state.swapcase()

try:
    if unprivileged == True:
        result['memory'] = int(open(cgroup_path + 'memory/' + getpass.getuser() + '/lxc/' + domain_name + '/memory.limit_in_bytes', 'r').read()) / 1024
        result['swap'] = (int(open(cgroup_path + 'memory/' + getpass.getuser() + '/lxc/' + domain_name + '/memory.memsw.limit_in_bytes', 'r').read()) / 1024) - result['memory']
    else:
        result['memory'] = int(open(cgroup_path + 'memory/lxc/' + domain_name + '/memory.limit_in_bytes', 'r').read()) / 1024
        result['swap'] = (int(open(cgroup_path + 'memory/lxc/' + domain_name + '/memory.memsw.limit_in_bytes', 'r').read()) / 1024) - result['memory']
except:
    result['memory'] = 0

result['vcpu'] = 0
result['ip_assignment'] = cont.get_ips(timeout = 2)

print json.dumps(result, separators = (',', ':'))
