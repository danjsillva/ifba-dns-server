import socket
import sys

IP = "127.0.0.1"

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, int(sys.argv[1])))

    client.send(sys.argv[2])

    data = client.recv(1024)
    response = data.rstrip("\r\n")

    print(response)

except Exception as e:
    print(e)
