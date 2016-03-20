from client import Client
import socket

#server = Server("127.0.0.1", 8000)
#server.run()

# Connect a new client

def clean_up_address(address):
    if address.startswith("http://"):
        address = address[7:]
    elif address.startswith("https://"):
        address = address[8:]

    return address

redirection_flag = 1

method = input("Please enter your desired HTTP method:\n")
method = method.upper()
input_address = input("Please enter your desired web-address:\n")

while redirection_flag == 1:
    redirection_flag = 0
    input_address = clean_up_address(input_address)
    client = Client(input_address, 80)

    print("Connected")

    message = ''.join(['a' for c in range(8100)]) + 'b'
    req = bytes(message, "utf-8")
    client.send(req, method)
    client.socket.shutdown(socket.SHUT_WR)

    # client2 = Client("127.0.0.1", 8000)
    # client2.send(bytes("client b", 'utf-8'))
    #
    # for i in range(10):
    #     c = Client("127.0.0.1", 8000)
    #     c.send(bytes("client " + str(i), 'utf-8'))
    #     c.close()

    reply = client.receive()

    if reply == b'':
        print("Server closed connection")
    else:
        if (str(reply, 'utf-8').find('302 Found') > 0) or (str(reply, 'utf-8').find('301 Moved Permanently') > 0):
            redirection_flag = 1
            method = 'GET'
            m_second = str(reply, 'utf-8')
            m_third = m_second[(m_second.find('Location')+10):]
            m_third = m_third[:m_third.find('\r\n')]
            print(m_third)
            input_address = m_third

        print("Server replied: " + str(reply, 'utf-8'))

client.close()
# client2.close()
