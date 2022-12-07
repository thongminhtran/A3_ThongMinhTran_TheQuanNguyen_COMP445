from abc import ABC, abstractmethod
from urllib.parse import urlsplit
import re
import socket
import ipaddress
from udp.UdpTransporter import UdpTransporter
from udp.RecWindow import RecWindow

class UDPRequest(ABC):
    def __init__(self, url, port, write_file, router_port, router_host, headers=[], verbose=False):
        self.url = url
        self.port = port
        self.host = ''
        self.headers = headers
        self.verbose = verbose
        self.connection = None
        self.write_file = write_file
        self.timeout = 1
        self.router_port = router_port
        self.router_host = router_host

    @abstractmethod
    def making_request(self, path, query, host):
        return

    def run(self, redirected=0):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        url_splitted = urlsplit(self.url)
        host = url_splitted.netloc
        port = self.port if ":" not in host else int(host[host.index(":") + 1:])
        self.port = port
        host = host if ":" not in url_splitted.netloc else host[0:host.index(":")]
        self.host = host
        path = url_splitted.path
        query = url_splitted.query
        query = "" if not query else "?" + query
        request = self.making_request(path, query, host)
        try:
            result = self.udp_request(request)
            redirection = self.status_response(result)
            if (redirection):
                if (redirected < 5):
                    self.run(redirected + 1)
                else:
                    print("Too many redirections, operation aborted")
        finally:
            self.connection.close()

    def udp_request(self, request):
        udp = UdpTransporter(
            self.timeout,
            router_addr=self.router_host,
            router_port=self.router_port,
            peer_ip=self.host,
            peer_port=self.port)
        udp.initialize_sh()
        sent_successfully = udp.donating(request)
        response = ""
        if (sent_successfully):
            response = udp.get_reply()
            self.connection.close()
        return response

    def status_response(self, response):
        status_code = re.findall(r"(?<=HTTP\/\d\.\d )(\d\d\d)", response)
        if (len(status_code) >= 1):
            status_code = int(status_code[0])
        if (status_code == 302):
            self.allocate(response)
            return True
        else:
            self.print_reply(response)
            return False
        return False



    def allocate(self, print_string):
        location = re.findall(r"(?<=Location\: )(.*)", print_string)
        if (len(location) > 0):
            location_str = str(location[0]).replace("\r", "")
            self.url = location_str
        else:
            print("Invalid location!!!")

    def print_reply(self, print_string):
        s = ""
        print('\n')
        if (self.verbose):
            s = print_string
        else:
            s = print_string[print_string.find("\r\n\r\n") + 1:]
        if self.write_file is not None:
            f = open(self.write_file, "w")
            f.write(s)
            f.close()
            print("The reply is located in " + self.write_file)
        else:
            print(s)
