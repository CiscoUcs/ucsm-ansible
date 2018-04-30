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
module: ucs_local_lun
short_description: Creates and deletes local luns via storage profile on Cisco UCS Manager
description:
- Creates and deletes local luns via storage profile on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify that the luns are  present and will create if needed.
    - If C(absent), will verify that the luns are absent and will delete if needed.
    choices: [present, absent]
    default: present

  name:
    description:
    - The name of the local LUN.
      This name can be between 1 and 10 alphanumeric characters. 
      Special characters other than -, _, : , and . Name cannot be changed after the object has been saved.
    - When creating multiple LUNs, name, start index as suffix to name and required number of LUNs can be specified as 
      comma separated values. 
    - For example, name: my_lun, 1, 60 - in this example 60 LUNs are created starting with the name my_lun1 to my_lun60.

  size:
    description:
    - Size of this LUN in GB. The size can range from 1 to 10240 GB.
    - Note: You do not need to specify a LUN size while claiming an orphaned LUN.

  auto_deploy:
    description:
    - Automatically deploys the local LUN.

  expand_to_avail:
    description:
    - Specifies that this LUN can be expanded to use the entire available disk group.
    - For each service profile, only one LUN can use this option.
    - Note: Expand To Available option is not supported for already deployed LUN.

  disk_policy_name:
    description:
    - Choose the disk group configuration to be applied to this local LUN from the drop-down list.
    - When creating multiple LUNs, the disk policy name is appended with the suffix as used in the LUN name.

requirements:
- ucsmsdk

author:
- sindhu sudhir (@sisudhir)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
ucs_local_lun:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: present
    name: my_lun
    size: my_lun_size
    disk_policy_name: my_dskgrp
    sp_name: my_stgprof

    ---

ucs_local_lun:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: absent
    name: my_lun
    size: my_lun_size
    disk_policy_name: my_dskgrp
    sp_name: my_stgprof

    ---

ucs_local_lun:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: present
    name: my_lun, name_start_index, num_luns
    size: my_lun_size
    disk_policy_name: my_dskgrp --> this parameter uses the name_start_index and num_luns as given in the local lun
    sp_name: my_stgprof

    ---

ucs_local_lun:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: absent
    name: my_lun, name_start_index, num_luns
    size: my_lun_size
    disk_policy_name: my_dskgrp --> this parameter uses the name_start_index and num_luns as given in the local lun
    sp_name: my_stgprof

    ---

    It's a best practice to use the -i option of ansible-playbook
    to specify an inventory file when configuring multiple hosts.

    When using an inventory file, the variables defined in the
    inventory file are used

ucs_local_lun:
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    state: "{{state}}"
    name: my_lun
    size: my_lun_size
    disk_policy_name: my_dskgrp
    sp_name: my_stgprof

    ---

ucs_local_lun:
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    state: "{{state}}"
    name: my_lun, name_start_index, num_luns
    size: my_lun_size
    disk_policy_name: my_dskgrp --> this parameter uses the name_start_index and num_luns as given in the local lun
    sp_name: my_stgprof
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec

def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(name=dict(type='str'),
                         size=dict(type='str'),
                         fractional_size=dict(type='str', default='0'),
                         auto_deploy=dict(type='str', default='auto-deploy', choices=['auto-deploy', 'no-auto-deploy']),
                         expand_to_avail=dict(type='str', default='no', choices=['yes', 'no']),
                         disk_policy_name=dict(type='str'),
                         sp_name=dict(type='str'),
                         state=dict(type='str', default='present', choices=['present', 'absent'])) 

    module = AnsibleModule(argument_spec,
                           supports_check_mode=True)
    ucs = UCSModule(module)

    from ucsmsdk.mometa.lstorage.LstorageDasScsiLun import LstorageDasScsiLun 

    num_luns = 1
    name_start_index = 0

    name_list = module.params['name'].split(',')
    lun_name_prefix = name_list[0]
    lun_name = lun_name_prefix
    if len( name_list ) == 3:
        name_start_index = int( name_list[1] )
        num_luns = int( name_list[2] )

    disk_policy_name_prefix = module.params['disk_policy_name'] 
    disk_policy_name = disk_policy_name_prefix

    for num in range( name_start_index, name_start_index + num_luns ):

        err = False
        changed = False
        mo_exists = False 

        if num_luns > 1:
            lun_name = lun_name_prefix + str( num )
            disk_policy_name = disk_policy_name_prefix + str( num )  

        try: 
            dn_base = 'org-root/profile-' + module.params['sp_name']
 
            mo = LstorageDasScsiLun(parent_mo_or_dn=dn_base,
                                name=lun_name,
                                size=module.params['size'], 
                                fractional_size=module.params['fractional_size'],
                                expand_to_avail=module.params['expand_to_avail'],
                                local_disk_policy_name=disk_policy_name)

            dn = dn_base + '/das-scsi-lun-' + lun_name 
            existing_mo = ucs.login_handle.query_dn(dn) 
            if existing_mo:
                # check top-level mo props
                kwargs = dict(size= module.params['size'])
                kwargs['fractional_size'] = module.params['fractional_size']
                kwargs['auto_deploy'] = module.params['auto_deploy']
                kwargs['expand_to_avail'] = module.params['expand_to_avail']
                kwargs['local_disk_policy_name'] = disk_policy_name 
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
