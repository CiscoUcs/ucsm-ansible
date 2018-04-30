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
module: ucs_disk_group_policy_auto 
short_description: Creates and deletes auto disk group policy on Cisco UCS Manager
description:
- Creates and deletes auto disk group policy on Cisco UCS Manager
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify that the auto disk group policy is present and will create if needed.
    - If C(absent), will verify that the auto disk group policy is absent and will delete if needed.
    choices: [present, absent]
    default: present
  
  name:
    description:
    - Name of the disk group policy
    - When creating multiple disk group policies, disk group policy name, start index as suffix to name and
      required number of policies can be specified as comma separated values.
    - For example, name: my_grp, 1, 60 - in this example 60 disk group policies are created
      starting with the name my_grp1 to my_grp60. 

  num_drives:
    description:
    - Specify the number of drives for the disk group. This can be from 0 to 24.

  num_ded_hot_spares:
    description:
    - Specify the number of hot spares for the disk group. This can be from 0 to 24.

  num_glob_hot_spares:
    description:
    - Specify the number of global hot spares for the disk group. This can be from 0 to 24.

  drive_type:
    description:
    - This can be one of the following:
      - Unspecified—Selects the first available drive type, and applies that to all drives in the group.
      - HDD—Hard disk drive
      - SDD—Solid state drive

  use_jbod_disks:
    description:
    - This can be one of the following:
      - Yes
      - No

  use_remaining_disks:
    description:
    - Specifies whether you can use all the remaining disks in the disk group or not.
 
  min_drive_size:
    description:
    - Enter the minimum drive size or unspecified to allow all drive sizes. This can be from 0 to10240 GB.

requirements:
- ucsmsdk

author:
- sindhu sudhir (@sisudhir)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
ucs_disk_group_policy_auto:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: present
    name: my_diskgrp
    num_drives: 4
    min_drive_size: 500

    ---

ucs_disk_group_policy_auto:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: absent
    name: my_diskgrp
    num_drives: 4
    min_drive_size: 500
    
    ---

ucs_disk_group_policy_auto:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: present
    name: my_grp, name_start_index, num_policies
    num_drives: 1
    min_drive_size: 500

    ---

ucs_disk_group_policy_auto:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: absent
    name: my_grp, name_start_index, num_policies
    num_drives: 1
    min_drive_size: 500

    ---

    It's a best practice to use the -i option of ansible-playbook
    to specify an inventory file when configuring multiple hosts.

    When using an inventory file, the variables defined in the
    inventory file are used

ucs_disk_group_policy_auto:
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    state: "{{state}}"
    name: my_diskgrp
    num_drives: 4
    min_drive_size: 500

    ---

ucs_disk_group_policy auto:
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    state: "{{state}}"
    name: my_grp, name_start_index, num_policies
    num_drives: 1
    min_drive_size: 500

'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec

def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(name=dict(type='str'),
                         num_drives=dict(type='str', default='1'),
                         num_ded_hot_spares=dict(type='str', default='unspecified'),
                         num_glob_hot_spares=dict(type='str', default='unspecified'),
                         drive_type=dict(type='str', default='unspecified', choice=['unspecified', 'HDD', 'SSD']),
                         use_jbod_disks=dict(type='str', default='no', choice=['yes', 'no']),
                         use_remaining_disks=dict(type='str', default='no', choice=['yes', 'no']),
                         min_drive_size= dict(type='str', default='unspecified'),
                         state=dict(type='str', default='present', choices=['present', 'absent'])) 

    module = AnsibleModule(argument_spec,
                           supports_check_mode=True)
    ucs = UCSModule(module)

    from ucsmsdk.mometa.lstorage.LstorageDiskGroupQualifier import LstorageDiskGroupQualifier 

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
            dn = dn_base + '/disk-group-config-' + policy_name 

            existing_mo = ucs.login_handle.query_dn(dn + '/disk-group-qual')
            if existing_mo:
                # check top-level mo props
                kwargs = dict(num_drives = module.params['num_drives'])
                kwargs['drive_type'] = module.params['drive_type']
                kwargs['use_jbod_disks'] = module.params['use_jbod_disks']
                kwargs['use_remaining_disks'] = module.params['use_remaining_disks']
                kwargs['num_ded_hot_spares'] = module.params['num_ded_hot_spares']
                kwargs['num_glob_hot_spares'] = module.params['num_glob_hot_spares']
                kwargs['min_drive_size'] = module.params['min_drive_size']
                if existing_mo.check_prop_match(**kwargs):
                    mo_exists = True
       
            mo_dg_qual = LstorageDiskGroupQualifier(parent_mo_or_dn=dn,
                                        num_drives=module.params['num_drives'],
                                        drive_type=module.params['drive_type'],
                                        use_jbod_disks=module.params['use_jbod_disks'],
                                        use_remaining_disks=module.params['use_remaining_disks'],
                                        num_ded_hot_spares=module.params['num_ded_hot_spares'],
                                        num_glob_hot_spares=module.params['num_glob_hot_spares'],
                                        min_drive_size=module.params['min_drive_size'])

            if module.params['state'] == 'absent':
                if mo_exists:
                    if not module.check_mode: 
                        # delete mo if dn already exist
                        ucs.login_handle.remove_mo(mo_dg_qual)
                        ucs.login_handle.commit()
                    changed = True               
            else:
                if not mo_exists:
                    if not module.check_mode:
                        # create mo if dn does not already exist
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
