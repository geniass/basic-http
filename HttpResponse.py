class HttpResponse:
    def __init__(self, sock, header):
        message = sock.recv(2048)
        if message == b'':
            print("Socket {0} closed\n".format(self.socket.getsockname()))
        else:
            print("buffer", repr(message))

        terminator = b'\r\n'

        header_end = message.find(terminator)
        header = str(message[:header_end], 'utf-8')
        header_list = [h.split(':') for h in header.split('\n')]
        headers = {h[0]:h[1] for h in header_list if len(h) == 2}
        print(headers,'\n')

        if 'Content-Length' in headers: self.content_length = int(headers['Content-Length'])

