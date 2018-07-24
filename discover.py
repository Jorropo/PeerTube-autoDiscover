#!/usr/bin/env python3
import json
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

toScan = []

if len(sys.argv) != 2:
    print("Wrong argument ammount, give one argument, entry node without https")
    sys.exit(2)

toScan.append(sys.argv[1])
allNode = toScan.copy()

try: #try for don't crash on ctrl + C
    while len(toScan) > 0:
        print("Staying to scan : " + str(len(toScan)))
        try: #try for don't crash on urllib fail
            searchIng = toScan.pop(0)
            for i in json.loads(urlopen(Request("https://"+searchIng+"/api/v1/server/following")).read().decode())["data"]:
                if not i in allNode:
                    allNode.append(i["following"]["host"])
                    toScan.append(i["following"]["host"])
                    print("Discovered : " + i["following"]["host"])
        except:
            pass
except:
    print("canceled")

for i in allNode:
    print(i)
