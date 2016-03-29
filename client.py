import socket
import HttpRequest
from socket_utils import recv_response
from ResourceHTMLParser import ResourceHTMLParser
import hashlib
import sys


def adjust_address(address):
    if address.startswith("https://"):
        sys.exit("\nUnfortunately this client cannot connect to secure servers. Goodbye!")

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

def get_proxy_compat_url(host, url, proxy_address):
        if proxy_address:
            return "http://" + host + url
        else:
            return url


class Client:

    def __init__(self, address, port, proxy_address, proxy_port, fetch_resources=False):
        self.host = get_host(adjust_address(address))
        # self.url = get_url(adjust_address(address), self.host)
        self.url = get_relative_url(adjust_address(address))
        self.port = port
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.fetch_resources = fetch_resources

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.reset_connection()

    def reset_connection(self):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.proxy_address:
            self.socket.connect((self.proxy_address, self.proxy_port))
        else:
            self.socket.connect((self.host, self.port))

    def save_all_resources(self, resource_urls):
        for resource in resource_urls:
            if not resource.startswith("http://"):
                continue

            print("Fetching: ", resource)
            host = get_host(adjust_address(resource))
            uri = get_relative_url(adjust_address(resource))
            uri = get_proxy_compat_url(host, uri, self.proxy_address)

            req = HttpRequest.HttpRequest()
            req.host = host
            req.uri = uri
            self.socket.sendall(req.gen_message())

            resource_response = recv_response(self.socket)
            filename = hashlib.sha1(
                resource_response.content).hexdigest()
            with open("temp/" + filename, "wb") as f:
                f.write(resource_response.content)
            if resource_response.connection == "close":
                self.reset_connection()

    def request(self, request):
        request.host = self.host
        request.uri = get_proxy_compat_url(self.host, self.url, self.proxy_address)
        print("This is the generated request in client:")
        print(request.gen_message())
        self.socket.sendall(request.gen_message())
        response = recv_response(self.socket)

        while response.status_code in (301, 302):
            print(response.gen_message())
            print("Redirecting to: " + response.location)
            redirect_addr = adjust_address(response.location)
            self.host = get_host(redirect_addr)
            self.url = get_url(redirect_addr, get_host(redirect_addr))

            req = HttpRequest.HttpRequest()
            req.host = self.host
            req.uri = get_proxy_compat_url(self.host, self.url, self.proxy_address)
            req.method = request.method
            # TODO: HttpRequest copy constructor
            print(req.gen_message())

            if response.connection == "close":
                self.reset_connection()
            self.socket.sendall(req.gen_message())
            response = recv_response(self.socket)

        if "text/html" in response.content_type and self.fetch_resources:
            if response.connection == "close":
                self.reset_connection()
            parser = ResourceHTMLParser()
            resources = parser.extract_resource_urls(str(response.content, "ISO-8859-1"))
            print("RESOURCES", resources)
            self.save_all_resources(resources)

        return response

    def close(self):
        self.socket.close()
