from client import Client
import socket
import sys
import HttpRequest
from datetime import datetime, timedelta

# Connect a new client
try:
    proxy_addr = input("Please input your proxy server addr: "
                       "(Leave blank if you do not require this)\n")

    if proxy_addr == '':
        proxy_port = 0
    else:
        try:
            proxy_port = int(input("Please enter your proxy port:\n"))
        except ValueError:
            sys.exit("\nPort number entered was not an integer. Please re-try")

    method = input("Please enter your desired HTTP method:\n")
    method = method.upper()
    method = method.replace(' ', '')

    input_address = input("Please enter your desired web-address:\n")

    if method == 'POST' or method == 'PUT':
        content = "Please enter the information you would like to " + method + ":\n"
        content = input(content)
    else:
        content = ''

    if method == 'CONDGET':
        try:
            last_mod = input("Please enter your desired last modified date check:(format: dd/mm/yyyy)\n")
            last_mod = datetime.strptime(last_mod, '%d/%m/%Y')
        except ValueError:
            sys.exit('You have incorrectly entered a date. Try again')
    else:
        last_mod = datetime.strptime('01/01/1000', '%d/%m/%Y')


    client = Client(input_address, 8000, proxy_addr, proxy_port, fetch_resources=True)

except (TimeoutError, ConnectionRefusedError):
    sys.exit("\nCould not connect to desired proxy server. "
          "Please re-check your proxy address and/or port number")

print("Connected")

req = HttpRequest.HttpRequest()
req.method = method
req.content = bytes(content, 'UTF-8')
req.if_mod_since = last_mod.strftime("%a, %d %b %Y %H:%M:%S GMT")
reply = client.request(req)

print(reply.gen_message())

client.socket.shutdown(socket.SHUT_WR)
client.close()
