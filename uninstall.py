#!/usr/bin/env python

import os
import sys
import shutil

try:
    import ansible
except:
    print("Ansible is not installed")
    sys.exit(1)

ansible_path = ansible.__path__[0]
module_utils = ansible_path + '/module_utils/'
extras_path = ansible_path + '/modules/extras'
server_path = extras_path + '/server'
ucs_path = server_path + '/cisco'
remote_management_module_utils = module_utils + '/remote_management/'

if os.path.isdir(server_path):
    shutil.rmtree(server_path)

if os.path.isfile(module_utils + 'cisco_ucs.py'):
    os.remove(module_utils + 'cisco_ucs.py')

if os.path.isfile(remote_management_module_utils + 'ucs.py'):
    os.remove(remote_management_module_utils + 'ucs.py')
