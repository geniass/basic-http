from client import Client
import socket
import sys
import HttpRequest

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("url", help="the url that will be requested")
parser.add_argument("--method", help="the HTTP method to use", default='GET')
parser.add_argument("--port", help="the web server's port", default=80)
parser.add_argument("--proxy_addr", help="the proxy server's address")
parser.add_argument(
    "--proxy_port", help="the proxy server's port", default=7000)
parser.add_argument("-i", "--interactive",
                    help="run in interactive mode (ignores other options)")
args = parser.parse_args()

proxy_addr = args.proxy_addr if args.proxy_addr else ""
proxy_port = args.proxy_port if args.proxy_port else 7000
method = args.method if args.method else "GET"
input_address = args.url if args.url else ""

if args.interactive:
    proxy_addr = input("Please input your proxy server addr: "
                       "(Leave blank if you do not require this)\n")
    if proxy_addr == '':
        proxy_port = 0
    else:
        try:
            proxy_port = int(input("Please enter your proxy port:\n"))
        except ValueError:
            print("\nPort number entered was not an integer. Please re-try")
            sys.exit(0)

    input_address = input("Please enter your desired web-address:\n")

    method = input("Please enter your desired HTTP method:\n")
    method = method.upper()
    method = method.replace(' ', '')

if method == 'POST' or method == 'PUT':
    content = "Please enter the information you would like to " + method + ":\n"
    content = input(content)
else:
    content = ''

try:
    client = Client(input_address, 80, proxy_addr, proxy_port)

except (TimeoutError, ConnectionRefusedError):
    print("\nCould not connect to desired proxy server. "
          "Please re-check your proxy address and/or port number")

    sys.exit(0)

print("Connected")

req = HttpRequest.HttpRequest()
req.method = method
req.content = content
reply = client.request(req)

print(reply.gen_message())

client.socket.shutdown(socket.SHUT_WR)
client.close()
