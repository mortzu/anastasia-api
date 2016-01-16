#! /usr/bin/env python

# Module for system functions
import sys

""" Module for operation system
    functions """
import os

import socket

import time

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
        # Make variables reachable
        global CLI_ARGS
        global VIRT_TYPE

        # Default HTTP code is 200
        http_code = 200

        if not self.path:
            # Continue running
            result = {'type': 'fatal', 'message': 'Not found'}
            http_code = 404
        else:
            # Parse URL parameters
            o = urlparse(self.path)

            url_parts = o.path.split('/')

            if (CLI_ARGS.api_key != self.headers.get('API-KEY')) and (CLI_ARGS.api_key != url_parts[1]):
                result = {'type': 'fatal', 'message': 'Unauthorized'}
                http_code = 403
            elif o.path == '/' or (CLI_ARGS.api_key == url_parts[1]):
                # instanciate class of virtual servers
                mod = __import__(VIRT_TYPE)
                class_ = getattr(mod, VIRT_TYPE)

                virt = class_(CLI_ARGS)

                # Informations about all domains requested
                result = virt.get_domains()
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

    def do_POST(self):
        # make variables reachable
        global CLI_ARGS
        global VIRT_TYPE

        # Default HTTP code is 200
        http_code = 200

        if (CLI_ARGS.api_key != self.headers.get('API-KEY')):
            result = {'type': 'fatal', 'message': 'Unauthorized'}
            http_code = 403
        elif not self.path:
            # Continue running
            result = {'type': 'fatal', 'message': 'Not found'}
            http_code = 404
        else:
            # Parse URL parameters
            o = urlparse(self.path)

            # instanciate class of virtual servers
            mod = __import__(VIRT_TYPE)
            class_ = getattr(mod, VIRT_TYPE)

            virt = class_(CLI_ARGS)

            splitted_url = o.path.split('/')

            if splitted_url[1] == 'start':
                http_code = virt.domain_start(splitted_url[2])
            elif splitted_url[1] == 'stop':
                http_code = virt.domain_stop(splitted_url[2])
            elif splitted_url[1] == 'shutdown':
                http_code = virt.domain_shutdown(splitted_url[2])
            elif splitted_url[1] == 'restart':
                http_code = virt.domain_stop(splitted_url[2])

                if http_code == 200:
                    time.sleep(2)
                    http_code = virt.domain_start(splitted_url[2])
            elif splitted_url[1] == 'reboot':
                http_code = virt.domain_reboot(splitted_url[2])
            else:
                result = {'type': 'fatal', 'message': 'Not found'}
                http_code = 404

            if http_code == 200:
                result = {'type': 'success', 'message': 'Task completed successful'}
            elif http_code == 404:
                result = {'type': 'fatal', 'message': 'Not found'}
            elif http_code == 500:
                result = {'type': 'fatal', 'message': 'Internal Server Error'}
            elif http_code == 501:
                result = {'type': 'fatal', 'message': 'Not Implemented'}

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
    CLI_ARGS = parser.parse_args()

    # Global variables
    VIRT_TYPE = CLI_ARGS.virtualization

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
