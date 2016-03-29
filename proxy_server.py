import socket
from server import ServerThread
from ProxyRequestHandler import ProxyRequestHandler

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
                print("\n***RECEIVED CONNECTION FROM CLIENT***.\n")
                ct = ServerThread(clientsocket,RequestHandlerClass=ProxyRequestHandler, allow_persistent=True)
                ct.start()

        except KeyboardInterrupt:
            self.socket.shutdown(socket.SHUT_RDWR)


if __name__ == '__main__':
    proxy_Server = proxy_server("127.0.0.1", 7000)
    proxy_Server.run()
