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
short_description: Creates and deletes disk group policy on Cisco UCS Manager
description:
- Creates and deletes disk group policy on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify that the disk group policy is present and will create if needed.
    - If C(absent), will verify that the disk group policy is absent and will delete if needed.
    choices: [present, absent]
    default: present

  name:
    description:
    - Name of the disk group policy
    - When creating multiple disk group policies, disk group policy name, start index as suffix to name and
      required number of policies can be specified as comma separated values.
    - For example, name: my_grp, 1, 60 - in this example 60 disk group policies are created 
      starting with the name my_grp1 to my_grp60. 
  
  raid_level:
    description:
    - The RAID level for the disk group policy. This can be one of the following:
      - RAID 1 Mirrored
      - RAID 0 Striped
      - RAID 5 Striped Parity
      - RAID 6 Striped Dual Parity
      - RAID 10 Mirrored and Striped
      - RAID 50 Striped Parity and Striped
      - RAID 60 Striped Dual Parity and Striped
    - Note:
      - When disk group with RAID 1 policy with four disks is created, storage 
        controller creates a RAID1E configuration internally.

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

    ---

ucs_disk_group_policy:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: absent 
    name: my_dskgrp
    raid_level: mirror
    
    ---

ucs_disk_group_policy:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: present
    name: my_grp, name_start_index, num_policies
    raid_level: stripe

    ---

ucs_disk_group_policy:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: absent
    name: my_grp, name_start_index, num_policies
    raid_level: stripe

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

    ---

ucs_disk_group_policy:
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    state: "{{state}}"
    name: my_grp, name_start_index, num_policies
    raid_level: stripe
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
                         state=dict(type='str', default='present', choices=['present', 'absent'])) 

    module = AnsibleModule(argument_spec,
                           supports_check_mode=True)
    ucs = UCSModule(module)

    from ucsmsdk.mometa.lstorage.LstorageDiskGroupConfigPolicy import LstorageDiskGroupConfigPolicy 

    num_policies = 1
    name_start_index = 0

    name_list = module.params['name'].split(',')
    policy_name_prefix = name_list[0]
    policy_name = policy_name_prefix
    if len( name_list ) == 3:
        name_start_index = int( name_list[1] )
        num_policies = int( name_list[2] )

    for num in range( name_start_index, name_start_index + num_policies ):

        err = False
        changed = False
        mo_exists = False
        if num_policies > 1:
            policy_name = policy_name_prefix + str( num )

        try:
            dn_base = 'org-root' 
            mo = LstorageDiskGroupConfigPolicy(parent_mo_or_dn=dn_base,
                                           name=policy_name,
                                           descr=module.params['descr'],
                                           raid_level=module.params['raid_level']) 

            dn = dn_base + '/disk-group-config-' + policy_name 
            existing_mo = ucs.login_handle.query_dn(dn)
            if existing_mo:
                # check top-level mo props
                kwargs = dict(descr= module.params['descr'])
                kwargs['raid_level'] = module.params['raid_level']
                if existing_mo.check_prop_match(**kwargs):
                    mo_exists = True
       
            if module.params['state'] == 'absent':
                if mo_exists:
                    if not module.check_mode: 
                        # delete mo if dn already exist
                        ucs.login_handle.remove_mo(mo)
                        ucs.login_handle.commit()
                    changed = True               
            else:
                 if not mo_exists:
                    if not module.check_mode:
                        # create mo if dn does not already exist
                        ucs.login_handle.add_mo(mo, True)
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
