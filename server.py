import sys
import socket
import thread
import csv
import time


CONFIG = []
TABLE = []
SERVER = None


def LoadConfig(serverName):
    try:
        global CONFIG

        fileReader = open(serverName + "-config.csv", "r")
        reader = csv.DictReader(fileReader)
        CONFIG = list(reader)[0]
        fileReader.close()

        print("Server loads config at " + serverName + "-config.csv file")

        return True
    except Exception as e:
        print(e)

        return False


def UpdateDataTable():
    try:
        global TABLE

        print("Server starts update data table service at " +
              CONFIG["servername"] + "-data-authoritative.csv and " +
              CONFIG["servername"] + "-data-recursive.csv files ")

        while True:
            fileReader = open(CONFIG["servername"] +
                              "-data-recursive.csv", "r")
            reader = csv.DictReader(fileReader)
            table = list(reader)
            fileReader.close()

            fileWriter = open(CONFIG["servername"] +
                              "-data-recursive.csv", "w+")
            writer = csv.DictWriter(fileWriter, fieldnames=[
                                    "name", "ip", "ttl"])

            writer.writeheader()

            for row in table:
                if int(row["ttl"]) == 0 or int(row["ttl"]) > time.time():
                    writer.writerow(row)

            fileWriter.close()

            LoadFromDataTable()

            time.sleep(int(CONFIG["ttu"]))
    except Exception as e:
        print(e)


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
    except Exception as e:
        print(e)

        return False


def LoadFromDataTable():
    try:
        global TABLE

        fileReader1 = open(CONFIG["servername"] +
                           "-data-authoritative.csv", "r")
        reader = csv.DictReader(fileReader1)
        TABLE = list(reader)
        fileReader1.close()

        fileReader2 = open(CONFIG["servername"] + "-data-recursive.csv", "r")
        reader = csv.DictReader(fileReader2)
        TABLE += list(reader)
        fileReader2.close()

        print("Server loads data table at " +
              CONFIG["servername"] + "-data-authoritative.csv and " +
              CONFIG["servername"] + "-data-recursive.csv files ")

        return True
    except Exception as e:
        print(e)

        return False


def AddToDataTable(domainName, domainIP, domainTTL):
    try:
        file = open(CONFIG["servername"] + "-data-recursive.csv", "a+")
        writer = csv.DictWriter(file, fieldnames=["name", "ip", "ttl"])
        writer.writerow({"name": domainName, "ip": domainIP,
                         "ttl": int(time.time()) + int(domainTTL)})
        file.close()

        print("Server updates data table at " +
              CONFIG["servername"] + "-data-recursive.csv file")

        LoadFromDataTable()
    except Exception as e:
        print(e)


def GetIpFromNameLocal(domainName):
    for row in TABLE:
        if row["name"] == domainName:
            print("Server finds IP " + row["ip"] + " for domain " + domainName)

            return row["ip"] + " " + row["ttl"]

    return False


def GetIpFromNameRoot(domainName):
    if CONFIG["servername"] != "root":
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((CONFIG["rootip"].split(":")[0],
                        int(CONFIG["rootip"].split(":")[1])))

        print("Server was connected to root server at IP " +
              CONFIG["rootip"].split(":")[0]) + ":" + CONFIG["rootip"].split(":")[1]

        client.send(domainName)

        data = client.recv(1024)
        response = data.rstrip("\r\n")

        client.close()

        if response != "404":
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((response.split()[0].split(":")[0],
                            int(response.split()[0].split(":")[1])))

            print("Server was connected to DNS server at IP " +
                  response.split(":")[0]) + ":" + response.split(":")[1]

            client.send(domainName)

            data = client.recv(1024)
            response = data.rstrip("\r\n")

            AddToDataTable(domainName, response.split()
                           [0], response.split()[1])

            return GetIpFromNameLocal(domainName)

    return False


if LoadConfig(sys.argv[1]):
    thread.start_new_thread(UpdateDataTable, ())

    if LoadServer():
        while True:
            connection, address = SERVER.accept()

            print("Server received connection from IP " +
                  str(address[0]) + ":" + str(address[1]))

            data = connection.recv(1024)
            domainName = data.rstrip("\r\n")

            connection.send(GetIpFromNameLocal(domainName)
                            or (GetIpFromNameRoot(domainName))
                            or "404")
