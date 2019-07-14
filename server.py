import sys
import socket
import thread
import csv
import time


CONFIG = None
SERVER = None
TABLE = None


def LoadConfig(serverName):
    try:
        global CONFIG

        file = open(serverName + "-config.csv", "r")
        reader = csv.DictReader(file)

        CONFIG = list(reader)[0]

        file.close()

        print("Server loads config at " + serverName + "-config.csv file")

        return True
    except Exception:
        print(Exception)

        return False


def LoadServer():
    try:
        global SERVER

        SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SERVER.bind((CONFIG["serverip"].split(":")[0],
                     int(CONFIG["serverip"].split(":")[1])))
        SERVER.listen(1)

        print("Server is running at " +
              CONFIG["serverip"].split(":")[0] + ":" + str(CONFIG["serverip"].split(":")[1]))

        return True
    except Exception:
        print(Exception)

        return False


def LoadTable():
    try:
        global TABLE

        file = open(CONFIG["servername"] + "-data.csv", "r")
        reader = csv.DictReader(file)

        TABLE = list(reader)

        file.close()

        print("Server loads data table at " +
              CONFIG["servername"] + "-data.csv file")

        return True
    except Exception:
        print(Exception)

        return False


def GetIpFromNameLocal(domainName):
    for row in TABLE:
        if row["name"] == domainName:
            print("Server finds IP " + row["ip"] + " for domain " + domainName)

            return row["ip"]

    return False


def GetIpFromNameRaiz(domainName):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((CONFIG["rootip"].split(":")[0],
                    int(CONFIG["rootip"].split(":")[1])))

    print("Server was connected to root server at IP " +
          CONFIG["rootip"].split(":")[0]) + ":" + CONFIG["rootip"].split(":")[1]

    client.send(domainName)

    data = client.recv(1024)
    response = data.rstrip("\r\n")

    client.close()

    if response != 404:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((response.split(":")[0],
                        int(response.split(":")[1])))

        print("Server was connected to DNS server at IP " +
              response.split(":")[0]) + ":" + response.split(":")[1]

        client.send(domainName)

        data = client.recv(1024)
        response = data.rstrip("\r\n")

    return response


if LoadConfig(sys.argv[1]):
    if LoadTable():
        if LoadServer():
            while True:
                connection, address = SERVER.accept()

                print("Server received connection from IP " +
                      str(address[0]) + ":" + str(address[1]))

                data = connection.recv(1024)
                domainName = data.rstrip("\r\n")

                connection.send(GetIpFromNameLocal(domainName)
                                or GetIpFromNameRaiz(domainName)
                                or 404)
