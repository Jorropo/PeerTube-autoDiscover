#!/usr/bin/env python3.7
#-----------------------------------------import
import json
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import aiohttp
import asyncio
from ptDiscover import discover, aff, fetch

async def main():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as s:
        instancesList = []
        #-----------------------------------------getting instances list status
        aff("getting instances list satus")
        for i in json.loads(
            await fetch(s,"https://instances.joinpeertube.org/api/v1/instances?start=0&count=" +
                str(json.loads(
                    await fetch(s,"https://instances.joinpeertube.org/api/v1/instances?start=0&count=0"
                ))["total"]
            )))["data"]:
            instancesList.append(i["host"])

        #-----------------------------------------argument processing
        if len(sys.argv) < 2 or len(sys.argv) > 3 :
            sys.stderr.write("Wrong argument ammount, give one argument, entry node without https, use instances list to seed\n")
            toScan = instancesList.copy()
        else:
            toScan = [sys.argv[1]]

        #-----------------------------------------result usage
        for i in await discover(toScan, s):
            if i not in instancesList:
                try:
                    urlopen(Request("https://instances.joinpeertube.org/api/v1/instances",urlencode({"host":i}).encode()),timeout=15).read().decode()
                    aff("Added " + i)
                except:
                    sys.stderr.write("instances list don't like me for node : " + i + "\n")

#-----------------------------------------run
asyncio.run(main())

#-----------------------------------------finish
sys.exit(0)
