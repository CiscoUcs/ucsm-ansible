#!/usr/bin/env python

import os
import sys

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


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def copy_files(src, dest):
    import shutil
    src_files = os.listdir(src)
    for file_name in src_files:
        src_file = os.path.join(src, file_name)
        dst_file = os.path.join(dest, file_name)
        if (os.path.isfile(src_file)):
            print(src_file, "===>", dst_file)
            shutil.copy(src_file, dst_file)

# Create the directory for the main module under extras/server/cisco repo
if not os.path.isdir(ucs_path):
    os.makedirs(ucs_path)
touch(server_path + '/__init__.py')
touch(ucs_path + '/__init__.py')

# Copy files from library folder to ucs_path
copy_files(os.getcwd() + '/library', ucs_path)

# Copy common files to module_util
copy_files(os.getcwd() + '/utils', module_utils)



