import socket
import thread
import sys
import json

IP = "127.0.0.1"
PORT = 3000
CLIENT = None


def LoadClient(portNumber):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((IP, int(portNumber)))

        return client
    except Exception:
        print(Exception)

        return None


CLIENT = LoadClient(sys.argv[1])

CLIENT.send(sys.argv[2])

data = CLIENT.recv(1024)
response = data.rstrip("\r\n")

print(response)
