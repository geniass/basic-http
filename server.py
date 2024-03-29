import socket
import threading
import sys
from pathlib import Path

from socket_utils import recv_request

import HttpResponse
from HttpMessage import BadRequestError
from ServerRequestHandler import ServerRequestHandler


class ServerThread(threading.Thread):

    def __init__(self, s, RequestHandlerClass, allow_persistent=True, static_dir="./static"):
        super(ServerThread, self).__init__()
        self.socket = s
        self.RequestHandlerClass = RequestHandlerClass
        self.allow_persistent = allow_persistent
        self.static_dir = Path(static_dir).resolve()

    def run(self):
        while True:
            try:
                req = recv_request(self.socket)
                print('\nThe received request is:\n' + str(req.gen_message(),'UTF-8'))

                handler = self.RequestHandlerClass(req, static_dir=self.static_dir)
                response = handler.handle()

                print("Response for", req.host, req.uri, response.status_code)

                # if the client requested persistent connections, and they are
                # allowed, then return Connection: keep-alive
                connection = req.connection if self.allow_persistent else "close"
                response.connection = connection

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
                # Client closed the connection, close our side now
                print(e, file=sys.stderr)
                break
            except OSError as e:
                print(e, file=sys.stderr)


class Server:
    """
    Generic server class that listens on a given port for incoming connections and creates a new thread for each
    new connection.
    An instance of RequestHandlerClass is instantiated to process each received request.
    This class can be used as a regular server, as well as the basis for a proxy server by using a different
    RequestHandler.
    """

    def __init__(self, address, port, RequestHandlerClass):
        self.RequestHandlerClass = RequestHandlerClass
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((address, port))
        self.socket.listen(5)

    def run(self):
        try:
            while True:
                clientsocket, clientaddr = self.socket.accept()
                print("Connected: {0}".format(clientaddr))
                ct = ServerThread(clientsocket, self.RequestHandlerClass, allow_persistent=True)
                ct.start()

        except KeyboardInterrupt:
            self.socket.shutdown(socket.SHUT_RDWR)


if __name__ == '__main__':
    server = Server("0.0.0.0", 8000, ServerRequestHandler)
    server.run()
