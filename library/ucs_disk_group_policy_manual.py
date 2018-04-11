#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: ucs_disk_group_policy_manual 
short_description: Creates and deletes manual disk group policy on Cisco UCS Manager
description:
- Creates and deletes manual disk group policy on Cisco UCS Manager
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify that the manual disk group policy is present and will create if needed.
    - If C(absent), will verify that the manual disk group policy is absent and will delete if needed.
    choices: [present, absent]
    default: present

  name:
    description:
    - Name of the disk group policy 
   
  disk_list:
    description:
    - List of disks 

  slot_num:
    description:
    - The slot number of the specific disk.

  role:
    description:
    - The role of the disk. This can be one of the following:
      - Normal
      - Ded Hot Spare
      - Glob Hot Spare

  span_id:
    description:
    - The Span ID of the specific disk.
  
  requirements:
- ucsmsdk

author:
- sindhu sudhir (@sisudhir)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
ucs_disk_group_policy_manual:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: present
    name: my_diskgrp
    disk_list:
      - slot_num: "1"
        role: "normal"
      - slot_num: "2"
        role: "normal"
      - slot_num: "3"
        role: "normal"
      - slot_num: "4"
        role: "normal"

    ---

ucs_disk_group_policy_manual:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: present
    name: my_diskgrp
    slot_num: "1"
    role: "normal"
    span_id: "1"

    ---

ucs_disk_group_policy_manual:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: absent
    name: my_diskgrp
    disk_list:
      - slot_num: "1"
        role: "normal"
      - slot_num: "2"
        role: "normal"
      - slot_num: "3"
        role: "normal"
      - slot_num: "4"
        role: "normal"
    
    ---

    It's a best practice to use the -i option of ansible-playbook
    to specify an inventory file when configuring multiple hosts.

    When using an inventory file, the variables defined in the
    inventory file are used

ucs_disk_group_policy_manual:
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    state: "{{state}}"
    name: my_diskgrp
    disk_list:
      - slot_num: "1"
        role: "normal"
      - slot_num: "2"
        role: "normal"
      - slot_num: "3"
        role: "normal"
      - slot_num: "4"
        role: "normal"

'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec

def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(name=dict(type='str'),
                         disk_list=dict(type='list'),
                         slot_num=dict(type='str'),
                         role=dict(type='str', default='normal'),
                         span_id=dict(type='str', default='unspecified'), 
                         state=dict(type='str', default='present', choices=['present', 'absent'])) 

    module = AnsibleModule(argument_spec,
                           supports_check_mode=True)
    ucs = UCSModule(module)

    from ucsmsdk.mometa.lstorage.LstorageLocalDiskConfigRef import LstorageLocalDiskConfigRef 
    err = False
    changed = False
    mo_exists = False

    try:
        if module.params['disk_list']:
            # directly use the list (single resource and list are mutually exclusive
            disk_list = module.params['disk_list']
        else:
            # single resource specified, create list from the current params
            disk_list = [module.params]

        for disk in disk_list:

            mo_exists = False
            commit = False

            if not disk.get('span_id'):
                disk['span_id'] = "unspecified" 

            if not disk.get('role'):
                disk['role'] = 'normal'

            dn_base = 'org-root' 
            dn = dn_base + '/disk-group-config-' + module.params['name'] 
      
            disk_mo = ucs.login_handle.query_dn(dn + '/slot-' + disk['slot_num'])
            if disk_mo:
                # check top-level mo props
                kwargs = dict(slot_num = disk['slot_num'])
                kwargs['role'] = disk['role']
                kwargs['span_id'] = disk['span_id']
                if disk_mo.check_prop_match(**kwargs):
                    mo_exists = True
        
            mo = LstorageLocalDiskConfigRef(parent_mo_or_dn=dn,
                                            slot_num=disk['slot_num'],
                                            role=disk['role'],
                                            span_id=disk['span_id'])

            if module.params['state'] == 'absent':
                if mo_exists:
                    if not module.check_mode:
                        # delete mo if dn already exists 
                        ucs.login_handle.remove_mo(mo)
                        commit = True
                    changed = True               
            else:
                if not mo_exists:
                    if not module.check_mode:
                        # create mo if dn does not already exist
                        ucs.login_handle.add_mo(mo)
                        commit = True
                    changed = True

        if commit:
            ucs.login_handle.commit()

    except Exception as e:
        err = True
        ucs.result['msg'] = "setup error: %s " % str(e)

    ucs.result['changed'] = changed
    if err:
        module.fail_json(**ucs.result)
    module.exit_json(**ucs.result)

if __name__ == '__main__':
    main()
