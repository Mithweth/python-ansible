# python-servicenow

Easily execute Ansible Task and Playbooks

## Installation

`python setup.py install`

## Unit tests

`python setup.py test`

## Usage

```
import pyansible
pb = pyansible.Playbook('playbook.yml', inventory='/etc/ansible/hosts')
if pb.run():
  print "Success!"
else:
  print "Failed!"
```
