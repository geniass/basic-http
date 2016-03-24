import socket
import HttpResponse
import HttpRequest
from socket_utils import recv_content
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

    def send(self, message, method, content):
        req = HttpRequest.HttpRequest()
        req.host = self.host
        req.uri = self.url
        req.content = bytes(content, 'ISO-8859-1')
        if method == '':
            # Default method
            req.method = 'GET'
        else:
            req.method = method
        req.user_agent = 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'
        print(req.gen_request())
        print(str(req.gen_request(), 'ISO-8859-1'))
        print(self.socket.sendall(req.gen_request()))

    @property
    def receive(self):
        message = self.socket.recv(2048)
        msg_str = str(message, 'ISO-8859-1')

        if message == b'':
            print("Socket {0} closed\n".format(self.socket.getsockname()))
            print("Server closed connection")
        else:
            print("Buffer", repr(message))
            while msg_str.find('HTTP/1.1 3') > -1:
                print("Server replied: " + msg_str)
                redirect_addr = msg_str[(msg_str.find('Location')+10):]
                redirect_addr = redirect_addr[:redirect_addr.find('\r\n')]

                print("Redirecting to: ",redirect_addr)
                input_address = redirect_addr

                self.url = get_url(adjust_address(input_address), self.host)

                message = ''.join(['a' for c in range(8100)]) + 'b'
                req = bytes(message, 'ISO-8859-1')
                self.send(req,'','')

                msg_str = str(self.socket.recv(2048), 'ISO-8859-1')

        message = bytes(msg_str,'ISO-8859-1')
        return message

    def close(self):
        self.socket.close()