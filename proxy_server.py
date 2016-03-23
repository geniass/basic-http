import socket
import threading
from client import Client


class proxy_server_thread(threading.Thread):
    def __init__(self, sock, allow_persistent=True):
        super(proxy_server_thread, self).__init__()
        self.socket = sock
        self.allow_persistent = allow_persistent

    def run(self):
        while True:
            message = self.socket.recv(2048)
            if message == b'':
                print("Peer {0} closed connection\n".format(self.socket.getpeername()))
                break
            else:
                message_str = str(message, 'UTF-8')
                print("\n***RECEIVED CONNECTION FROM CLIENT***.\n\nThe received request is:\n", message_str)

            method = message_str.split("/")[0]
            method = method.replace(' ', '')

            host = message_str[(message_str.find('Host:') + 6):]
            host = host[:host.find('\r\n')]

            uri = message_str[(message_str.find(method) + len(method) + 1):]
            uri = uri[:(uri.find('HTTP/1.1') - 1)]
            input_address = host + uri

            print("This proxy server is now going to take the client to: ", input_address)

            print('\n***MAKING REQUEST FOR CLIENT...***\n')
            prox_client = Client(input_address, 80, '', 0)
            message = ''.join(['a' for c in range(8100)]) + 'b'
            req = bytes(message, "utf-8")
            prox_client.send(req, method)

            server_reply = prox_client.receive()

            if server_reply == b'':
                print("Server closed connection")
            else:
                print("Server replied: " + str(server_reply, encoding="ISO-8859-1"))

            print('\n***PROXY SERVER FORWARDING RESPONSE BACK TO CLIENT***\n')
            self.socket.sendall(server_reply)

class Proxy_server:
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
                client_thread = proxy_server_thread(clientsocket, allow_persistent=True)
                client_thread.start()

        except KeyboardInterrupt:
            self.socket.shutdown(socket.SHUT_RDWR)


if __name__ == '__main__':
    prox_server = Proxy_server("127.0.0.1", 7000)
    prox_server.run()
