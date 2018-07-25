# peertube-autoDiscover
Auto discover new peertube node by your self, this program isn't depends of a nodes list.

Doesn't require human intervantion for discovering new nodes, how ? This program ask to each already known node her list of known nodes and retry until all nodes were discovered.

This make it a little slow, (2-15 minutes execution time), if you do it with cron you shouldn't lunch it more than one each hours.

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
