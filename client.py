import socket

sock = socket.socket()
host = "192.168.43.104"
port = 12360

sock.connect((host, port))
print sock.recv(4096)

while True:
    user_input = raw_input("Enter your vote")
    sock.send(user_input)

sock.close()
