import socket
import threading
import sys

from socket_utils import recv_content


class ServerThread(threading.Thread):
    def __init__(self, s):
        super(ServerThread, self).__init__()
        self.socket = s

    def run(self):
        try:
            while True:
                message = self.socket.recv(2048)
                if message == b'':
                    print("Socket {0} closed\n".format(self.socket.getsockname()))
                    break

                terminator = b'\r\n'

                header_end = message.find(terminator)
                header = str(message[:header_end], 'utf-8')
                header_list = [h.split(':') for h in header.split('\n')]
                headers = {h[0]:h[1] for h in header_list if len(h) == 2}

                m = b'Here is some data to send back'

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

                reply = bytes("Content-Length:{0}\r\n\r\n".format(len(m)), 'utf-8') + m
                result = self.socket.sendall(reply)
        except ConnectionError as e:
            print(e, file=sys.stderr)
        except OSError as e:
            print(e, file=sys.stderr)


class Server:
    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((address, port))
        self.socket.listen(5)

    def run(self):
        while True:
            clientsocket, clientaddr = self.socket.accept()
            print("Connected: {0}".format(clientaddr))
            ct = ServerThread(clientsocket)
            ct.start()


if __name__ == '__main__':
    server = Server("127.0.0.1", 8000)
    server.run()
