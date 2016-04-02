import socket
import sys
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
            return "http://" + adjust_address(host) + url
        else:
            return url


class Client:

    def __init__(self, address, port, proxy_address, proxy_port, fetch_resources=False):
        self.host = get_host(adjust_address(address))
        self.url = get_relative_url(adjust_address(address))
        self.port = port
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.fetch_resources = fetch_resources

        self.allow_persistent = True
        if "wits.ac.za" in address and not proxy_address:
            print("You are trying to access wits.ac.za. Persistent connections are not available")
            self.allow_persistent = False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.reset_connection()

    def reset_connection(self):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.proxy_address:
            self.socket.connect((self.proxy_address, self.proxy_port))
        else:
            self.socket.connect((self.host, self.port))

    def request_and_redirect(self, request):
        request.connection = "keep-alive" if self.allow_persistent else "close"
        self.socket.sendall(request.gen_message())
        response = recv_response(self.socket)

        while response.status_code in (301, 302):
            print("Redirecting to: " + response.location)
            redirect_addr = adjust_address(response.location)
            host = get_host(redirect_addr)
            url = get_url(redirect_addr, get_host(redirect_addr))

            req = HttpRequest.HttpRequest()
            req.host = host
            req.uri = get_proxy_compat_url(host, url, self.proxy_address)
            req.method = request.method
            request.connection = "keep-alive" if self.allow_persistent else "close"
            # TODO: HttpRequest copy constructor

            if response.connection == "close" or not self.allow_persistent:
                self.reset_connection()

            self.socket.sendall(req.gen_message())
            response = recv_response(self.socket)
        return response

    def save_all_resources(self, resource_urls):
        for resource in resource_urls:
            if resource.startswith("https://"):
                continue

            print("Fetching: ", resource)
            host = get_host(adjust_address(resource))
            host = host if host else self.host
            uri = get_relative_url(adjust_address(resource))
            uri = get_proxy_compat_url(host, uri, self.proxy_address)

            req = HttpRequest.HttpRequest()
            req.host = host
            req.uri = uri
            resource_response = self.request_and_redirect(req)

            filename = hashlib.sha1(
                resource_response.content).hexdigest()
            with open("temp/" + filename, "wb") as f:
                f.write(resource_response.content)
            if resource_response.connection == "close" or not self.allow_persistent:
                self.reset_connection()

    def request(self, request):
        request.host = self.host
        request.uri = get_proxy_compat_url(self.host, self.url, self.proxy_address)

        response = self.request_and_redirect(request)
        if response.location:
            self.host = get_host(adjust_address(response.location))

        if "text/html" in response.content_type and self.fetch_resources:
            if response.connection == "close" or not self.allow_persistent:
                self.reset_connection()
            parser = ResourceHTMLParser()
            resources = parser.extract_resource_urls(str(response.content, "ISO-8859-1"))
            print("RESOURCES", resources)
            self.save_all_resources(resources)

        return response

    def close(self):
        self.socket.close()
