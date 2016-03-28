import socket
import HttpRequest
from socket_utils import recv_response
import sys
from ResourceHTMLParser import ResourceHTMLParser


def adjust_address(address):
    if address.startswith("https://"):
        sys.exit(
            "\nUnfortunately this client cannot connect to secure servers. Goodbye!")

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

    def request(self, request):
        request.host = self.host
        request.uri = self.url
        self.socket.sendall(request.gen_message())
        response = recv_response(self.socket)

        while response.status_code in (301, 302):
            print(response.gen_message())
            print("Redirecting to: " + response.location)
            redirect_addr = adjust_address(response.location)
            req = HttpRequest.HttpRequest()
            req.uri = get_url(redirect_addr, get_host(redirect_addr))
            req.host = get_host(redirect_addr)
            print(redirect_addr)
            req.method = request.method
            # TODO: HttpRequest copy constructor
            print(req.gen_message())

            self.reset_connection(get_host(redirect_addr), self.port)
            self.socket.sendall(req.gen_message())
            response = recv_response(self.socket)

        parser = ResourceHTMLParser()
        resources = parser.extract_resource_urls(
            str(response.content, "utf-8"))
        print("RESOURCES", resources)
        for resource in resources:
            # send request for resource
            # receive file
            # save somewhere
            req = HttpRequest.HttpRequest()
            request.host = self.host
            req.uri = resource
            self.socket.sendall(req.gen_message())
            resource_response = recv_response(self.socket)
            filename = resource.replace("/", "_")
            with open("temp/" + filename, "wb") as f:
                f.write(resource_response.content)

        return response

    def close(self):
        self.socket.close()
