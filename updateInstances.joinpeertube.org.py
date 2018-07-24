#!/usr/bin/env python3
import json
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

toScan = []
allNode = []
instancesList = []

if len(sys.argv) != 2:
    sys.stderr.write("Wrong argument ammount, give one argument, entry node without https\n")
    sys.exit(2)

toScan.append(sys.argv[1])
allNode.append(sys.argv[1])

for i in json.loads(urlopen(Request("https://instances.joinpeertube.org/api/v1/instances?start=0&count="+str(json.loads(urlopen(Request("https://instances.joinpeertube.org/api/v1/instances?start=0&count=0"), timeout=15).read().decode())["total"])), timeout=15).read().decode())["data"]:
    instancesList.append(i["host"])

try: #try for don't crash on ctrl + C
    while len(toScan) > 0:
        searchIng = toScan.pop(0)
        try: #try for don't crash on urllib fail
            for i in json.loads(urlopen(Request("https://"+searchIng+"/api/v1/server/following?count="+str(json.loads(urlopen(Request("https://"+searchIng+"/api/v1/server/following?count=0"), timeout=15).read().decode())["total"])), timeout=15).read().decode())["data"]:
                if i["following"]["host"] not in allNode and i["state"] == "accepted":
                    allNode.append(i["following"]["host"])
                    toScan.append(i["following"]["host"])
        except KeyboardInterrupt:
            raise Exception('Pass out this error.')
        except:
            allNode.remove(searchIng)
            sys.stderr.write("error on contacting " + searchIng + "\n")
except:
    sys.stderr.write("canceled\n")

for i in allNode:
    if i not in instancesList:
        try:
            urlopen(Request("https://instances.joinpeertube.org/api/v1/instances",urlencode({"host":i}).encode())).read().decode()
        except:
            sys.stderr.write("instances list don't like me\n")
        sys.stdout.write(i+"\n")
