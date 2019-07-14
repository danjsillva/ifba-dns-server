import socket
import thread
import sys
import csv


IP = "127.0.0.1"
PORT = 3000
SERVER = None
TABLE = None


def LoadServer(portNumber):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((IP, int(portNumber)))
        server.listen(1)

        print("Server is running at " + IP + ":" + str(portNumber))

        return server
    except Exception:
        print(Exception)

        return None


def LoadTable(tableName):
    file = open(tableName, "r")
    table = csv.DictReader(file)

    print("Server loads table " + tableName)

    return table


try:
    SERVER = LoadServer(sys.argv[1])

    TABLE = LoadTable(sys.argv[2])

    for line in TABLE:
        print(line)

    while True:
        connection, address = SERVER.accept()
        print("Server received connection from IP " + str(address))

        data = connection.recv(1024)
        name = data.rstrip("\r\n")

        # ip = getIpFromName(name)

        # connection.send(ip or "404")

except Exception as e:
    print(e)
