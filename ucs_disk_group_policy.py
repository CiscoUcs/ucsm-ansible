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
module: ucs_disk_group_policy
short_description: Creates and deletes storage profile on Cisco UCS Manager
description:
- Creates disk group policy on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify that the storage profile is present and will create if needed.
    - If C(absent), will verify that the storage profile is absent and will delete if needed.
    choices: [present, absent]
    default: present
  name:
    description:
    - Name of the disk group policy
requirements:
- ucsmsdk
author:
- sindhu sudhir (@sisudhir)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
ucs_disk_group_policy:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: present
    name: my_dskgrp
    raid_level: mirror
    num_drives: 2

    ---

ucs_disk_group_policy:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: absent
    name: my_dskgrp
    raid_level: mirror
    num_drives: 2
    
    ---

    It's a best practice to use the -i option of ansible-playbook
    to specify an inventory file when configuring multiple hosts.

    When using an inventory file, the variables defined in the
    inventory file are used

ucs_disk_group_policy:
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    state: "{{state}}"
    name: my_dskgrp
    raid_level: mirror
    num_drives: 2
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec

def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(name=dict(type='str'),
                         descr=dict(type='str', default=''),
                         raid_level=dict(type='str', default='stripe', choices=['stripe', 'mirror', 'mirror-stripe', 'stripe-parity', 'stripe-dual parity', 'stripe-parity-stripe', 'stripe-dual-parity-stripe'] ),
                         num_drives=dict(type='str', default='1'),
                         num_ded_hot_spares=dict(type='str', default='unspecified'),
                         num_glob_hot_spares=dict(type='str', default='unspecified'),
                         drive_type=dict(type='str', default='unspecified', choice=['unspecified', 'HDD', 'SSD']),
                         use_jbod_disks=dict(type='str', default='no', choice=['yes', 'no']),
                         use_remaining_disks=dict(type='str', default='no', choice=['yes', 'no']),
                         min_drive_size= dict(type='str', default='unspecified'),
                         state=dict(type='str', default='present', choices=['present', 'absent'])) 

    module = AnsibleModule(argument_spec,
                           supports_check_mode=False)
    ucs = UCSModule(module)

    from ucsmsdk.mometa.lstorage.LstorageDiskGroupQualifier import LstorageDiskGroupQualifier 
    from ucsmsdk.mometa.lstorage.LstorageDiskGroupConfigPolicy import LstorageDiskGroupConfigPolicy 
    err = False
    changed = False

    try:
        dn_base = 'org-root' 
        mo = LstorageDiskGroupConfigPolicy(parent_mo_or_dn=dn_base,
                                           name=module.params['name'],
                                           descr=module.params['descr'],
                                           raid_level=module.params['raid_level']) 

        dn = dn_base + '/disk-group-config-' + module.params['name'] 
        dn_exists = ucs.login_handle.query_dn(dn)

        mo_dg_qual = LstorageDiskGroupQualifier(parent_mo_or_dn=dn,
                                                num_drives=module.params['num_drives'],
                                                drive_type=module.params['drive_type'],
                                                use_jbod_disks=module.params['use_jbod_disks'],
                                                use_remaining_disks=module.params['use_remaining_disks'],
                                                num_ded_hot_spares=module.params['num_ded_hot_spares'],
                                                num_glob_hot_spares=module.params['num_glob_hot_spares'],
                                                min_drive_size=module.params['min_drive_size'])

        if module.params['state'] == 'absent':
            if dn_exists: 
                # delete mo if dn already exist
                ucs.login_handle.remove_mo(mo_dg_qual)
                ucs.login_handle.remove_mo(mo)
                ucs.login_handle.commit()
                changed = True               
        else:
            if not dn_exists:
                # create mo if dn does not already exist
                ucs.login_handle.add_mo(mo, True)
                ucs.login_handle.add_mo(mo_dg_qual, True)
                ucs.login_handle.commit()
                changed = True

    except Exception as e:
        err = True
        ucs.result['msg'] = "setup error: %s " % str(e)

    ucs.result['changed'] = changed
    if err:
        module.fail_json(**ucs.result)
    module.exit_json(**ucs.result)

if __name__ == '__main__':
    main()
