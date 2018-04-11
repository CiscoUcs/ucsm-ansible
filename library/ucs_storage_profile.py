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
module: ucs_storage_profile
short_description: Creates and deletes storage profile on Cisco UCS Manager
description:
- Creates storage profile on Cisco UCS Manager.
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
    - Name of the storage profile
requirements:
- ucsmsdk
author:
- sindhu sudhir (@sisudhir) 
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
ucs_storage_profile:
    hostname: 10.0.1.10 
    username: my_username 
    password: my_password 
    state: present 
    name: my_stgprof 

    ---

ucs_storage_profile:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    state: absent 
    name: my_stgprof 

    ---

    It's a best practice to use the -i option of ansible-playbook 
    to specify an inventory file when configuring multiple hosts.

    When using an inventory file, the variables defined in the 
    inventory file are used

ucs_storage_profile: 
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    state: "{{state}}"
    name: my_stgprof 
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
                         state=dict(type='str', default='present', choices=['present', 'absent'])) 

    module = AnsibleModule(argument_spec,
                           supports_check_mode=True)
    ucs = UCSModule(module)

    from ucsmsdk.mometa.lstorage.LstorageProfile import LstorageProfile 
    err = False
    changed = False
    mo_exists = False 

    try:
        dn_base = 'org-root'
        mo = LstorageProfile(parent_mo_or_dn=dn_base,
                             name=module.params['name'],
                             descr=module.params['descr'])

        dn = dn_base + '/profile-' + module.params['name']
        existing_mo = ucs.login_handle.query_dn(dn) 
        if existing_mo: 
            # check top-level mo props
            kwargs = dict(descr = module.params['descr'])
            kwargs['name'] = module.params['name'] 
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
