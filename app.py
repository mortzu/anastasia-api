#! /usr/bin/env python

# Module for system functions
import sys

""" Module for operation system
    functions """
import os

import socket

""" append directory with
    virtualization to path """
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/Virtualizations/')

# Module which parses commandline arguments
import argparse

# Webserver library
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# Threading server
from SocketServer import ThreadingMixIn

# Parse URLs
from urlparse import urlparse, parse_qs

# Parse and create JSON
import json

# Client handler class
class clientHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Default HTTP code is 200
        http_code = 200

        # If no data received
        if not self.path:
            # Continue running
            result = {'type': 'fatal', 'message': 'Not found'}
            http_code = 404
        else:
            # Parse URL parameters
            o = urlparse(self.path)
            tmp = parse_qs(o.query)
            """ remove [0] from parsed URL parameters
                and parse arguments """
            get_data = dict([(key, value[0]) for (key, value) in tmp.iteritems()])

            # Dictionary for result
            result = {}

            # Check for parameter action in GET request
            if 'action' in get_data:
                # make variables rechable
                global API_KEY
                global LIBVIRT_URI
                global SSH_CONSOLE
                global VIRT_TYPE

                # instanciate class of virtual servers
                mod = __import__(VIRT_TYPE)
                class_ = getattr(mod, VIRT_TYPE)

                if VIRT_TYPE == 'Digitalocean':
                    virt = class_(DIGITALOCEAN_TOKEN, SSH_CONSOLE)
                elif VIRT_TYPE == 'SolusVM':
                    virt = class_(SOLUSVM_KEY, SOLUSVM_HASH, SSH_CONSOLE)
                elif VIRT_TYPE == 'Scaleway':
                    virt = class_(SCALEWAY_KEY, SSH_CONSOLE)
                elif VIRT_TYPE == 'OpenVZ':
                    virt = class_()
                else:
                    virt = class_(LIBVIRT_URI, SSH_CONSOLE)

                # informations about all domains requested?
                if get_data['action'] == 'get_domains':
                    result = virt.get_domains()
                elif get_data['action'] == 'domain_start' and get_data['name'] != '':
                    virt.domain_start(get_data['name'])
                elif get_data['action'] == 'domain_shutdown' and get_data['name'] != '':
                    virt.domain_shutdown(get_data['name'])
                elif get_data['action'] == 'domain_reboot' and get_data['name'] != '':
                    virt.domain_reboot(get_data['name'])
                elif get_data['action'] == 'domain_reset' and get_data['name'] != '':
                    virt.domain_destroy(get_data['name'])
                    time.sleep(2)
                    virt.domain_start(get_data['name'])
                else:
                    result = {'type': 'fatal', 'message': 'Not found'}
                    http_code = 404
            else:
                result = {'type': 'fatal', 'message': 'Not found'}
                http_code = 404

        # return HTTP status
        self.send_response(http_code)
        self.send_header('Content-type', 'application/json')
        # end of headers
        self.end_headers()
        # return JSON
        self.wfile.write(json.dumps(result, separators=(',', ':')))

# create threading HTTP server
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    address_family = socket.AF_INET6
    pass

# main method
if __name__ == '__main__':
    # instanciate argument parser
    parser = argparse.ArgumentParser()
    # add argument to parser
    parser.add_argument('--virtualization', action = 'store', help = 'Which virtualization is used', required = True)
    # add argument to parser
    parser.add_argument('--api-key', action = 'store', help = 'API key for authentication', required = True)
    # add argument to parser
    parser.add_argument('--libvirt-uri', action = 'store', help = 'URI for libvirt', default = 'qemu:///system')
    # add argument to parser
    parser.add_argument('--digitalocean-token', action = 'store', help = 'API token')
    # add argument to parser
    parser.add_argument('--scaleway-key', action = 'store', help = 'API key')
    # add argument to parser
    parser.add_argument('--solusvm-key', action = 'store', help = 'API key')
    # add argument to parser
    parser.add_argument('--solusvm-hash', action = 'store', help = 'API hash')
    # add argument to parser
    parser.add_argument('--enable-ssh-console', action = 'store_true', help = 'Enable SSH console with OpenVZ')
    """ parse arguments and store
        them to arguments dict """
    results = parser.parse_args()

    # Global variables
    VIRT_TYPE = results.virtualization
    API_KEY = results.api_key
    LIBVIRT_URI = results.libvirt_uri
    DIGITALOCEAN_TOKEN = results.digitalocean_token
    SCALEWAY_KEY = results.scaleway_key
    SOLUSVM_KEY = results.solusvm_key
    SOLUSVM_HASH = results.solusvm_hash
    SSH_CONSOLE = results.enable_ssh_console

    """ Check if given virtualization
        exists """
    try:
        __import__(VIRT_TYPE)
    except:
        print 'virt not found'
        sys.exit(1)

    # Create Webserver
    server = ThreadingHTTPServer(('::', 65535), clientHandler)
    # and run
    server.serve_forever()
