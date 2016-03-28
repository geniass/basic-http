import socket
import HttpRequest
from socket_utils import recv_response
import sys
from ResourceHTMLParser import ResourceHTMLParser
import hashlib
import os.path


def adjust_address(address):
    if address.startswith("https://"):
        print("\nUnfortunately this client cannot connect to secure servers. Goodbye!")

    if address.startswith("http://"):
        address = address[7:]

    return address


def get_host(url):
    return url.split("/")[0]


def get_url(url, host):

    uri = "".join(url.rsplit(host))
    if uri == '':
        uri = "/"

    return uri


def get_relative_url(url):
    rel_url = "/"
    first_slash = url.find("/")
    if first_slash >= 0:
        rel_url = url[first_slash:]
    return rel_url


class Client:

    def __init__(self, address, port, proxy_address, proxy_port):
        self.host = get_host(adjust_address(address))
        self.url = get_url(adjust_address(address), self.host)
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if proxy_address == '':
            self.socket.connect((self.host, port))
        else:
            self.socket.connect((proxy_address, proxy_port))

    def reset_connection(self, address, port):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))

    def save_all_resources(self, resource_urls):
        for resource in resource_urls:
            # send request for resource
            # receive file
            # save somewhere
            print("Fetching: ", resource)
            req = HttpRequest.HttpRequest()
            req.host = get_host(adjust_address(resource))
            req.uri = get_relative_url(adjust_address(resource))
            self.socket.sendall(req.gen_message())
            resource_response = recv_response(self.socket)
            filename, extension = os.path.splitext(resource)
            filename = hashlib.sha1(
                resource_response.content).hexdigest() + extension
            # with open("temp/" + filename, "wb") as f:
            #     f.write(resource_response.content)
            if resource_response.connection == "close":
                self.reset_connection(self.host, self.port)

    def request(self, request):
        request.host = self.host
        request.uri = self.url
        self.socket.sendall(request.gen_message())
        response = recv_response(self.socket)

        while response.status_code in (301, 302):
            print(response.gen_message())
            print("Redirecting to: " + response.location)
            redirect_addr = adjust_address(response.location)
            self.host = get_host(redirect_addr)
            req = HttpRequest.HttpRequest()
            req.uri = get_url(redirect_addr, get_host(redirect_addr))
            req.host = self.host
            print(redirect_addr)
            req.method = request.method
            # TODO: HttpRequest copy constructor
            print(req.gen_message())

            self.reset_connection(get_host(redirect_addr), self.port)
            self.socket.sendall(req.gen_message())
            response = recv_response(self.socket)

        parser = ResourceHTMLParser()
        resources = parser.extract_resource_urls(str(response.content, "ISO-8859-1"))
        print("RESOURCES", resources)
        self.save_all_resources(resources)

        return response

    def close(self):
        self.socket.close()
