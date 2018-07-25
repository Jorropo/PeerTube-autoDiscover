#!/usr/bin/env python3
#-----------------------------------------import
import json
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

#-----------------------------------------global declaration
toScan = []
allNode = []
instancesList = []
key = []

#-----------------------------------------key conf loading
if not os.path.exists("secret.json"):
    print("you don't have any key configuration, let's do one right know")#use print for crash with broken pipe if there isn't any conf
    st = '{\n    account:"'+input("account name (with admin right) ? ")+'",\n    password:"'+input("accout password ? ")+'"\n}'#use a temp string for one step make memory foot print bigger but if user cancel this no empty file will be created
	f = open("secret.json","w")
	f.write(st)
	f.close()
f = open("secret.json","r")
key = json.loads(f.read())
f.close()

#-----------------------------------------argument processing
if len(sys.argv) != 2:
    sys.stderr.write("Wrong argument ammount, give one argument, entry node without https, use instances list to seed\n")
    for i in json.loads(urlopen(Request("https://instances.joinpeertube.org/api/v1/instances?start=0&count="+str(json.loads(urlopen(Request("https://instances.joinpeertube.org/api/v1/instances?start=0&count=0"), timeout=15).read().decode())["total"])), timeout=15).read().decode())["data"]:
        instancesList.append(i["host"])
    toScan = instancesList.copy()
else:
    toScan.append(sys.argv[1])

allNode = toScan.copy()

#-----------------------------------------discovery
try: #try for don't crash on ctrl + C
    while len(toScan) > 0:
        searchIng = toScan.pop(0)
        try: #try for don't crash on urllib fail
            for i in json.loads(urlopen(Request("https://"+searchIng+"/api/v1/server/following?count="+str(json.loads(urlopen(Request("https://"+searchIng+"/api/v1/server/following?count=0"), timeout=15).read().decode())["total"])), timeout=15).read().decode())["data"]:
                t = i["following"]["host"]
                if t not in allNode:
                    allNode.append(t)
                    toScan.append(t)
            for i in json.loads(urlopen(Request("https://"+searchIng+"/api/v1/server/followers?count="+str(json.loads(urlopen(Request("https://"+searchIng+"/api/v1/server/followers?count=0"), timeout=15).read().decode())["total"])), timeout=15).read().decode())["data"]:
                t = i["followers"]["host"]
                if t not in allNode:
                    allNode.append(t)
                    toScan.append(t)
        except KeyboardInterrupt:
            raise Exception('Pass out this error.')
        except:
            allNode.remove(searchIng)
            sys.stderr.write("error on contacting " + searchIng + "\n")
except:
    sys.stderr.write("canceled\n")

#-----------------------------------------result usage
for i in allNode:
    sys.stdout.write(i+"\n")

#-----------------------------------------finish
sys.exit(1)
