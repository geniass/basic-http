import socket
import threading
import sys

from socket_utils import recv_content

import HttpRequest


class ServerThread(threading.Thread):
    def __init__(self, s, allow_persistent=True):
        super(ServerThread, self).__init__()
        self.socket = s
        self.allow_persistent = allow_persistent

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

                terminator = b'\r\n'

                header_end = message.find(terminator)
                header = str(message[:header_end], 'utf-8')
                header_list = [h.split(':') for h in header.split('\n')]
                headers = {h[0]:h[1] for h in header_list if len(h) == 2}

                m = b'<html><body><h1>Here is some data to send back</h1></body></html>'

                # req = HttpResponse.HttpResponse(self.socket, header)
                #
                # if req.data:
                #     print(repr(req.data))
                #     m = bytes(str(req.data, 'utf-8').upper(), 'utf-8')

                if 'Content-Length' in headers:
                    content_length = int(headers['Content-Length'])
                    chunks = bytearray(message[header_end+len(terminator):])
                    chunks.extend(recv_content(self.socket, content_length - len(chunks)))

                    print("chunks len", len(chunks))
                    print(repr(chunks))
                    m = bytes(str(chunks, 'utf-8').upper(), 'utf-8')

                if req.uri == '/favicon.ico':
                    reply = bytes("HTTP/1.1 404 Not found\r\nConnection: close\r\n\r\n", 'utf-8')
                else:
                    connection = req.connection if self.allow_persistent else "close"
                    reply = bytes("HTTP/1.1 200 OK\r\nContent-Length:{0}\r\nConnection: {1}\r\n\r\n".format(len(m), connection), 'utf-8') + m

                print(reply)
                self.socket.sendall(reply)

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
