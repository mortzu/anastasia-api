#! /usr/bin/env python2

# library for system functions
import sys

# library for filesystem functions
import os

# library for IP sockets
import socket

""" append directory with
    virtualization to path """
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/Virtualizations/')

# module which parses commandline arguments
import argparse

# webserver library
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# threading server
from SocketServer import ThreadingMixIn

# parse URLs
from urlparse import urlparse, parse_qs

# parse and create JSON
import json

# client handler class
class clientHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # default http code is 200
        http_code = 200

        # no data received
        if not self.path:
            # continue running
            result = {'type': 'fatal', 'message': 'Not found'}
            http_code = 404
        else:
            # parsing URL parameters
            o = urlparse(self.path)
            tmp = parse_qs(o.query)
            """ remove [0] from parsed URL parameters
                and parse arguments """
            get_data = dict([(key, value[0]) for (key, value) in tmp.iteritems()])

            # dictionary for result
            result = {}

            # check for parameter action in GET request
            if 'action' in get_data:
                # make variables rechable
                global VIRT_TYPE
                global API_KEY
                global LIBVIRT_URI

                # instanciate class of virtual servers
                mod = __import__(VIRT_TYPE)
                class_ = getattr(mod, VIRT_TYPE)
                virt = class_(LIBVIRT_URI)

                # informations about all domains requested?
                if get_data['action'] == 'get_domains':
                    result = virt.get_domains()
                elif get_data['action'] == 'domain_start' and get_data['name'] != '':
                    virt.domain_start(get_data['name'])
                elif get_data['action'] == 'domain_shutdown' and get_data['name'] != '':
                    virt.domain_shutdown(get_data['name'])
                elif get_data['action'] == 'domain_reboot' and get_data['name'] != '':
                    virt.domain_reboot(get_data['name'])
                else:
                    result = {'type': 'fatal', 'message': 'Not found'}
                    http_code = 404
            else:
                result = {'type': 'fatal', 'message': 'Not found'}
                http_code = 404

        """ return HTTP status
            200 is status for OK """
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
    """ parse arguments and store
        them to arguments dict """
    results = parser.parse_args()

    # 
    VIRT_TYPE = results.virtualization
    API_KEY = results.api_key
    LIBVIRT_URI = results.libvirt_uri

    """ try to import choosen virtualization class
        if failed print error message """
    try:
        __import__(VIRT_TYPE)
    except:
        print 'virt not found'
        sys.exit(1)

    # start webserver
    server = ThreadingHTTPServer(('::', 65535), clientHandler)
    server.serve_forever()
