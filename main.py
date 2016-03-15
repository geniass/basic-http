from client import Client
import socket

#server = Server("127.0.0.1", 8000)
#server.run()

client = Client("beta.is-an-engineer.com", 80)
print("Connected")
message = ''.join(['a' for c in range(8100)]) + 'b'
req = bytes(message, "utf-8")
client.send(req)
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
print("Server replied: " + str(reply, 'utf-8'))
client.close()
# client2.close()
