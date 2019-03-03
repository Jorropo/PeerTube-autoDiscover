#!/usr/bin/env python3
#-----------------------------------------import
import json
import sys
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

#-----------------------------------------global declaration
toScan = []
allNode = []
goodNode = []
instancesList = []
key = []
def getListFollowing(test):
    nc = json.loads(urlopen(Request("https://"+test+"/api/v1/server/following?count=0"), timeout=15).read().decode())["total"]
    nt = []
    for i in range(0,nc,100):
        for i in json.loads(urlopen(Request("https://"+test+"/api/v1/server/following?count=100&start="+str(i)), timeout=15).read().decode())["data"]:
            nt.append(i["following"]["host"])
    return nt
def getListFollowers(test):
    nc = json.loads(urlopen(Request("https://"+test+"/api/v1/server/followers?count=0"), timeout=15).read().decode())["total"]
    nt = []
    for i in range(0,nc,100):
    for i in json.loads(urlopen(Request("https://"+test+"/api/v1/server/followers?count=100&start="+str(i)), timeout=15).read().decode())["data"]:
        nt.append(i["follower"]["host"])
    return nt

#-----------------------------------------key conf loading
os.chdir(os.path.dirname(os.path.realpath(__file__)))
if not os.path.exists("secret.json"):
    print("you don't have any key configuration, let's do one right know")#use print for crash with broken pipe if there isn't any conf
    st = '{\n    "node":"'+input("node name (without https://) ? ")+'",\n    "account":"'+input("account name (with admin right) ? ")+'",\n    "password":"'+input("accout password ? ")+'"\n}\n'#use a temp string for one step make memory foot print bigger but if user cancel this no empty file will be created
    f = open("secret.json","w")
    f.write(st)
    f.close()
f = open("secret.json","r")
key = json.loads(f.read())
f.close()

toScan.append(key["node"])
allNode = toScan.copy()

#-----------------------------------------discovery
try: #try for don't crash on ctrl + C
    while len(toScan) > 0:
        searchIng = toScan.pop(0)
        try: #try for don't crash on urllib fail
            for i in getListFollowing(searchIng):
                if i not in allNode:
                    allNode.append(i)
                    toScan.append(i)
            for i in getListFollowers(searchIng):
                if i not in allNode:
                    allNode.append(i)
                    toScan.append(i)
            goodNode.append(searchIng)
        except KeyboardInterrupt:
            raise Exception('Pass out this error.')
        except:
            sys.stderr.write("error on contacting " + searchIng + "\n")
except:
    sys.stderr.write("canceled\n")

#-----------------------------------------leave and error on empty list
allNode.remove(key["node"])#don't send them self to the node we are seeding
if len(goodNode) == 0:
    sys.stderr.write("node other node than original were found, you must follow or been followed by an already integrated node\n")
    sys.exit(3)

#-----------------------------------------result usage
r = json.loads(urlopen(Request("https://"+key["node"]+"/api/v1/oauth-clients/local"),timeout=15).read().decode())
token = json.loads(urlopen(Request("https://"+key["node"]+"/api/v1/users/token",urlencode({"client_id":r["client_id"],"client_secret":r["client_secret"],"grant_type":"password","response_type":"code","username":key["account"],"password":key["password"]}).encode()),timeout=15).read().decode())
urlopen(Request("https://"+key["node"]+"/api/v1/server/following",(json.dumps({"hosts":goodNode})+"\n").encode("ascii"),headers={"Authorization":"Bearer "+token["access_token"],"Content-Type":"application/json"}),timeout=15).read().decode()
#-----------------------------------------finish
sys.exit(0)
