import socket
import threading
import sys
from pathlib import Path
from server import ServerThread

from socket_utils import recv_message

import HttpResponse
from HttpMessage import BadRequestError
from ProxyRequestHandler import ProxyRequestHandler


class proxy_server_thread(threading.Thread):

    def __init__(self, s, RequestHandlerClass=ProxyRequestHandler, allow_persistent=True, static_dir="./static"):
        super(proxy_server_thread, self).__init__()
        self.socket = s
        self.RequestHandlerClass = RequestHandlerClass
        self.allow_persistent = allow_persistent
        self.static_dir = Path(static_dir).resolve()

    def run(self):
        while True:
            try:
                print("\n***RECEIVED CONNECTION FROM CLIENT***.\n")
                # Receive request from client
                req = recv_message(self.socket)
                print('\nThe received request is:\n' + str(req.gen_message(),'UTF-8'))

                # Get response in handler
                handler = self.RequestHandlerClass(req, static_dir=self.static_dir)
                response = handler.handle()

                print("This is the handler response:")
                print(str(response.gen_message(), 'UTF-8'))
                # if the client requested persistent connections, and they are
                # allowed, then return Connection: keep-alive
                connection = req.connection if self.allow_persistent else "close"
                response.connection = connection

                # print(response.gen_message())
                self.socket.sendall(response.gen_message())

                if "keep-alive" not in req.connection.lower() or not self.allow_persistent:
                    print("Closing connection")
                    self.socket.shutdown(socket.SHUT_RDWR)
                    self.socket.close()
                    break

            except BadRequestError:
                response = HttpResponse.HttpResponse()
                response.status_code = 400
                response.reason = "Bad request"
                self.socket.sendall(response.gen_message())
            except ConnectionError as e:
                print(e, file=sys.stderr)
                break
            except OSError as e:
                print(e, file=sys.stderr)


class proxy_server:

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
                ct = ServerThread(clientsocket,RequestHandlerClass=ProxyRequestHandler, allow_persistent=True)
                ct.start()

        except KeyboardInterrupt:
            self.socket.shutdown(socket.SHUT_RDWR)


if __name__ == '__main__':
    proxy_Server = proxy_server("127.0.0.1", 7000)
    proxy_Server.run()
