from client import Client
import socket
import sys

# Connect a new client
try:
    proxy_addr = input("Please input your proxy server addr: (Leave blank if you do not require this)\n")

    if proxy_addr == '':
        proxy_port = 0
    else:
        try:
            proxy_port = int(input("Please enter your proxy port:\n"))
        except ValueError:
            print ("\nPort number entered was not an integer. Please re-try")
            sys.exit(0)

    method = input("Please enter your desired HTTP method:\n")
    method = method.upper()
    method = method.replace(' ', '')

    input_address = input("Please enter your desired web-address:\n")

    if method == 'POST' or method == 'PUT':
        content = "Please enter the information you would like to " + method.lower() + ":\n"
        content = input(content)
    else:
        content = ''

    client = Client(input_address, 80, proxy_addr, proxy_port)

except (TimeoutError,ConnectionRefusedError):
    print ("\nCould not connect to desired proxy server. Please re-check your proxy address and/or port number")
    sys.exit(0)

print("Connected")

message = ''.join(['a' for c in range(8100)]) + 'b'
req = bytes(message, 'ISO-8859-1')
client.send(req, method, content)

reply = client.receive

if reply == b'':
    print("Server closed connection")
else:
    print("Server replied: " + str(reply, 'ISO-8859-1'))

client.socket.shutdown(socket.SHUT_WR)
client.close()