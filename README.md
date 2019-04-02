# peertube-autoDiscover
Auto discover new peertube node by your self, this program isn't depends of a nodes list.

Doesn't require human intervantion for discovering new nodes, how ? This program ask to each already known node her list of known nodes and retry until all nodes were discovered.

It use asyncio to request multiple nodes at the same time.

## Usage
```sh
./discover.py [starting node list]
```
Then node list will by outputed in stdout, stderr contain error.

If no node is given it will use the instances list to seed.
### Example
```sh
./discover.py peertube.jorropo.ovh
```
```sh
./discover.py #use instances list to seed
```
# Install
You must install aiohttp and you should install aiodns to speed up dns resolution.
```
sudo python3.7 -m pip install aiohttp aiodns
```
You also need python 3.7 if you don't have it already (at the time I write this lines, default python3 on ubuntu is 3.6)
```
sudo apt install python3.7
```
# Update a node
For that to work you must follow or be followed by an already integrated node (manualy a node that follow other like peertube.jorropo.ovh)

This script can't be lunched by cron the first time (cause it will ask you question for create a json config file, secret.json).
```sh
./updateANode.py
```
If you would do secret.json file manualy here is a template (for be sure to don't be have conflict with web interface you should create a new administrator account named script and only used by script) :
```json
{
    "node":"URL OF YOUR NODE WITHOUT HTTPS://",
    "account":"ACCOUNT NAME WITH ADMIN RIGHT",
    "password":"PASSWORD OF THIS ACCOUNT"
}
```
Example :
```json
{
    "node":"peertube.jorropo.ovh",
    "account":"script",
    "password":"123456"
}
```
# Instances List update
Use it as the same of discover but you don't need to do somethings with stdout, this program will update instances list.

# Error ?
If you see some ssl errors, this is a wrong configuration with this node, this is harmless and they should be catched by a try but right now there is a bug with this.
