#!/usr/bin/env python3.7
#-----------------------------------------import
import json
import sys
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from ptDiscover import discoverSync

#-----------------------------------------global declaration
instancesList = []
key = []

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

#-----------------------------------------Discover
goodNode = discoverSync([key["node"]])

#-----------------------------------------leave and error on empty list
goodNode.remove(key["node"])#don't send them self to the node we are seeding
if len(goodNode) == 0:
    sys.stderr.write("node other node than original were found, you must follow or been followed by an already integrated node\n")
    sys.exit(3)

#-----------------------------------------result usage
r = json.loads(urlopen(Request("https://"+key["node"]+"/api/v1/oauth-clients/local"),timeout=15).read().decode())
token = json.loads(urlopen(Request("https://"+key["node"]+"/api/v1/users/token",urlencode({"client_id":r["client_id"],"client_secret":r["client_secret"],"grant_type":"password","response_type":"code","username":key["account"],"password":key["password"]}).encode()),timeout=15).read().decode())
urlopen(Request("https://"+key["node"]+"/api/v1/server/following",(json.dumps({"hosts":goodNode})+"\n").encode("ascii"),headers={"Authorization":"Bearer "+token["access_token"],"Content-Type":"application/json"}),timeout=15).read().decode()
#-----------------------------------------finish
sys.exit(0)
