# peertube-autoDiscover
Auto discover new peertube node

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
# Instances List update
Use it as the same of discover but you don't need to do somethings with stdout, this program will update instances list.
