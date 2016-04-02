import socket
from server import Server
from ProxyRequestHandler import ProxyRequestHandler

if __name__ == '__main__':
    proxy_Server = Server("0.0.0.0", 7000, ProxyRequestHandler)
    proxy_Server.run()
