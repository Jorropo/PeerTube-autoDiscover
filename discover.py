#!/usr/bin/env python3.7
#-----------------------------------------import
import json
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from ptDiscover import discoverSync

#-----------------------------------------global declaration
toScan = []

#-----------------------------------------argument processing
if len(sys.argv) != 2:
    sys.stderr.write("Wrong argument ammount, give one argument, entry node without https, use instances list to seed\n")
    for i in json.loads(urlopen(Request("https://instances.joinpeertube.org/api/v1/instances?start=0&count="+str(json.loads(urlopen(Request("https://instances.joinpeertube.org/api/v1/instances?start=0&count=0"), timeout=15).read().decode())["total"])), timeout=15).read().decode())["data"]:
        toScan.append(i["host"])
else:
    toScan = [sys.argv[1]]

#-----------------------------------------result usage
for i in discoverSync(toScan):
    sys.stdout.write(i+"\n")

#-----------------------------------------finish
sys.exit(0)
