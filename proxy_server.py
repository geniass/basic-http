import socket
import threading
from client import Client
import dataset
import caching
import HttpRequest

class proxy_server_thread(threading.Thread):
    def __init__(self, sock, allow_persistent=True):
        super(proxy_server_thread, self).__init__()
        self.socket = sock
        self.allow_persistent = allow_persistent

    def run(self):
        db = dataset.connect('sqlite:///cache.db')
        cache = db['user']

        # Receive request from client
        message = self.socket.recv(2048)
        message_str = str(message, 'ISO-8859-1')

        # Check if request is already in cache
        request_status = caching.check_if_cache_fresh(message_str, cache)

        # If not in cache, or object in cache is outdated, make request again
        if request_status == 'Not found' or request_status == 'Outdated cache. Request again':
            print('Request not previously in cache, or cached response is outdated')
            server_reply = make_request_for_client(message)

            # Made request again, now save in cache, IF cache-able
            caching.save_in_cache(message_str, server_reply, cache)

        else: #Request found in database and is fresh
            server_reply = request_status

        # Obtained response, now forward to client
        print('\n***PROXY SERVER FORWARDING RESPONSE BACK TO CLIENT***\n')
        self.socket.sendall(server_reply)
        print("testing socket send")

# Function to make request desired by client
def make_request_for_client(request):
    request_str = str(request, 'ISO-8859-1')

    if request == b'':
        print("Peer closed connection\n")
    else:
        print("\n***RECEIVED CONNECTION FROM CLIENT***.\n\nThe received request is:\n", request_str)

    method = request_str.split("/")[0]
    method = method.replace(' ', '')

    host = request_str[(request_str.find('Host:') + 6):]
    host = host[:host.find('\r\n')]

    uri = request_str[(request_str.find(method) + len(method) + 1):]
    uri = uri[:(uri.find('HTTP/1.0') - 1)]

    input_address = host + uri

    if method == 'POST' or method == 'PUT':
        content = request_str[(request_str.find('\r\n\n') + 3):]
    else:
        content = ''

    print("This proxy server is now going to take the client to: ", input_address)

    print('\n***MAKING REQUEST FOR CLIENT...***\n')
    prox_client = Client(input_address, 80, '', 0)

    # request = ''.join(['a' for c in range(8100)]) + 'b'
    # req = bytes(request, 'ISO-8859-1')

    req = HttpRequest.HttpRequest()
    req.method = method
    req.content = content
    server_reply = prox_client.request(req)

    print(str(server_reply.gen_message(), 'UTF-8'))

    return server_reply.gen_message()


class Proxy_server:
    # Intialise
    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((address, port))
        self.socket.listen(5)

    # Multithreading
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

# if(str(server_reply, 'ISO-8859-1').find('Expires:')) > -1:
#     expiry_date = str(server_reply, 'ISO-8859-1')[str(server_reply, 'ISO-8859-1').find('Expires') + 9:]
#     expiry_date = expiry_date[:expiry_date.find('\r\n')]
#     if (expiry_date == '-1'):
#         print('This page CANNOT be cached')
#     print(expiry_date)