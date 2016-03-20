import socket
import HttpResponse
import HttpRequest
from socket_utils import recv_content

def get_host(url):
        return url.split("/")[0]

def get_url(url, host):
    url2 = "".join(url.rsplit(host))
    if url2 == '':
        url2 = "/"

    return  url2

class Client:

    def __init__(self, address, port):
        self.host = get_host(address)
        self.url = get_url(address, self.host)
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, port))

    def send(self, message):
        req = HttpRequest.HttpRequest()
        req.host = self.host
        req.url = self.url
        req.user_agent = 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'
        # req = bytes("Content-Length:{0}\r\n".format(len(message)), "utf-8")
        # req += message
        # print(str(req, 'utf-8'))
        print(req.gen_request())
        print(str(req.gen_request(), 'utf-8'))
        print(self.socket.sendall(req.gen_request()))

    def receive(self):
        message = self.socket.recv(2048)
        if message == b'':
            print("Socket {0} closed\n".format(self.socket.getsockname()))
        else:
            print("buffer", repr(message))

        terminator = b'\r\n'

        # header_end = message.find(terminator)
        # header = str(message[:header_end], 'utf-8')
        # resp = HttpResponse.HttpResponse(header)

        return (message)

    def close(self):
        self.socket.close()
