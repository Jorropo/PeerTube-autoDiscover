#!/usr/bin/env python3
#-----------------------------------------import
import json
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

#-----------------------------------------global declaration
toScan = []
allNode = []
goodNode = []
instancesList = []
def aff(msg):
    if "--verbose" in sys.argv:
        sys.stdout.write(msg + "\n")

#-----------------------------------------getting instances list status
aff("getting instances list satus")
for i in json.loads(urlopen(Request("https://instances.joinpeertube.org/api/v1/instances?start=0&count="+str(json.loads(urlopen(Request("https://instances.joinpeertube.org/api/v1/instances?start=0&count=0"), timeout=15).read().decode())["total"])), timeout=15).read().decode())["data"]:
    instancesList.append(i["host"])

#-----------------------------------------argument processing
if len(sys.argv) < 2 or len(sys.argv) > 3 :
    sys.stderr.write("Wrong argument ammount, give one argument, entry node without https, use instances list to seed\n")
    toScan = instancesList.copy()
else:
    toScan.append(sys.argv[1])

allNode = toScan.copy()

#-----------------------------------------discovery
try: #try for don't crash on ctrl + C
    while len(toScan) > 0:
        searchIng = toScan.pop(0)
        aff("Searching for " + searchIng + ", " + str(len(toScan)) + " staying.")
        try: #try for don't crash on urllib failfail
            for i in json.loads(urlopen(Request("https://"+searchIng+"/api/v1/server/following?count="+str(json.loads(urlopen(Request("https://"+searchIng+"/api/v1/server/following?count=0"), timeout=15).read().decode())["total"])), timeout=15).read().decode())["data"]:
                t = i["following"]["host"]
                if t not in allNode:
                    aff("Discovered " + t)
                    allNode.append(t)
                    toScan.append(t)
            for i in json.loads(urlopen(Request("https://"+searchIng+"/api/v1/server/followers?count="+str(json.loads(urlopen(Request("https://"+searchIng+"/api/v1/server/followers?count=0"), timeout=15).read().decode())["total"])), timeout=15).read().decode())["data"]:
                t = i["follower"]["host"]
                if t not in allNode:
                    aff("Discovered " + t)
                    allNode.append(t)
                    toScan.append(t)
            goodNode.append(searchIng)
        except KeyboardInterrupt:
            raise Exception('Pass out this error.')
        except:
            sys.stderr.write("error on contacting " + searchIng + "\n")
except:
    sys.stderr.write("canceled\n")

#-----------------------------------------result usage
for i in goodNode:
    if i not in instancesList:
        try:
            urlopen(Request("https://instances.joinpeertube.org/api/v1/instances",urlencode({"host":i}).encode()),timeout=15).read().decode()
            aff("Added " + i)
        except:
            sys.stderr.write("instances list don't like me for node : " + i + "\n")

#-----------------------------------------finish
sys.exit(0)
