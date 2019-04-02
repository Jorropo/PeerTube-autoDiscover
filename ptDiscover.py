import json
import aiohttp
import asyncio
from asyncio import create_task as do
import sys

#-----------------------------------------global declaration
global allNode
allNode = []
global goodNode
goodNode = []
def aff(msg):
    if "--verbose" in sys.argv:
        sys.stdout.write(msg + "\n")
async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()
async def search(s, test, via):
    aff("Discovered " + test + " via " + via)
    global allNode
    global goodNode
    localTasks = []
    try:
        nc = json.loads(await fetch(s, "https://"+test+"/api/v1/server/following?count=0"))["total"]
        for i in range(0,nc,100):
            for i in json.loads(await fetch(s,"https://"+test+"/api/v1/server/following?count=100&start="+str(i)))["data"]:
                node = i["following"]["host"]
                if node not in allNode:
                    allNode.append(node)
                    localTasks.append(do(search(s, node, test)))
        nc = json.loads(await fetch(s,"https://"+test+"/api/v1/server/followers?count=0"))["total"]
        for i in range(0,nc,100):
            for i in json.loads(await fetch(s,"https://"+test+"/api/v1/server/followers?count=100&start="+str(i)))["data"]:
                node = i["follower"]["host"]
                if node not in allNode:
                    allNode.append(node)
                    localTasks.append(do(search(s, node, test)))
        goodNode.append(test)
    except:
        sys.stderr.write("Error on contacting " + test + "\n")
    for i in localTasks:
        await i

async def discover(toScan,s):
    global goodNode
    allNode = toScan.copy()
    #-----------------------------------------discovery
    localTasks = []
    for i in toScan:
        localTasks.append(do(search(s,i, "root")))

    for i in localTasks:
        await i
    return goodNode

async def _discover(toScan):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as s:
        await discover(toScan, s)

def discoverSync(toScan):
    global goodNode
    l = asyncio.get_event_loop()
    l.run_until_complete(_discover(toScan))
    l.close()
    return goodNode
