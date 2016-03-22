import socket
import threading
import sys

from socket_utils import recv_content

import HttpRequest
import HttpResponse


class ServerThread(threading.Thread):
    def __init__(self, s, allow_persistent=True):
        super(ServerThread, self).__init__()
        self.socket = s
        self.allow_persistent = allow_persistent

    def handle_get(self, request, response):
        m = b'<html><body><h1>Here is some data to send back</h1></body></html>'
        if request.uri == '/favicon.ico':
            response.status_code = 404
            response.reason = "Not found"
            response.content = b"Go Away"
        else:
            response.content = m

    def handle_head(self, request, response):
        self.handle_get(request, response)
        # HEAD should return headers only
        response.content_length = len(response.content)
        response.content = b""

    def run(self):
        try:
            while True:
                message = self.socket.recv(2048)
                if message == b'':
                    print("Peer {0} closed connection\n".format(self.socket.getpeername()))
                    break

                req = HttpRequest.HttpRequest(message)
                print("Request from:", self.socket.getpeername())
                print(str(req.gen_request(), "utf-8"))
                # TODO: use request

                connection = req.connection if self.allow_persistent else "close"
                response = HttpResponse.HttpResponse()
                response.connection = connection

                method = req.method
                if method == "GET":
                    self.handle_get(req, response)
                elif method == "HEAD":
                    self.handle_head(req, response)
                elif method == "POST":
                    pass
                elif method == "PUT":
                    pass
                elif method == "DELETE":
                    pass

                print(response.gen_response())
                self.socket.sendall(response.gen_response())

                if "keep-alive" not in req.connection.lower() or not self.allow_persistent:
                    print("Closing connection")
                    self.socket.shutdown(socket.SHUT_RDWR)
                    self.socket.close()
                    break

        except ConnectionError as e:
            print(e, file=sys.stderr)
        except OSError as e:
            print(e, file=sys.stderr)


class Server:
    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((address, port))
        self.socket.listen(5)

    def run(self):
        try:
            while True:
                clientsocket, clientaddr = self.socket.accept()
                print("Connected: {0}".format(clientaddr))
                ct = ServerThread(clientsocket, allow_persistent=True)
                ct.start()

        except KeyboardInterrupt:
            self.socket.shutdown(socket.SHUT_RDWR)


if __name__ == '__main__':
    server = Server("127.0.0.1", 8000)
    server.run()
