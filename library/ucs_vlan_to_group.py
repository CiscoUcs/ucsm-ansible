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
module: ucs_vlan_to_group
short_description: Add VLANs to a VLAN Group
description:
- Add VLANs to VLAN Groups on Cisco UCS Manager.
options:
  state:
    description:
    - If C(present), will verify VLANs are present and will create if needed.
    - If C(absent), will verify VLANs are absent and will delete if needed.
    choices: [present, absent]
    default: present
  vlanname:
    description:
    - The name assigned to the VLAN.
    - The VLAN name is case sensitive.
    - This name can be between 1 and 32 alphanumeric characters.
    - "You cannot use spaces or any special characters other than - (hyphen), \"_\" (underscore), : (colon), and . (period)."
    required: yes
  vlangroup:
    description:
    - The name assigned to the VLAN Group.
    - The VLAN Group name is case sensitive.
    - This name can be between 1 and 32 alphanumeric characters.
    - "You cannot use spaces or any special characters other than - (hyphen), \"_\" (underscore), : (colon), and . (period)."
    required: yes
requirements:
- ucsmsdk
author:
- Derrick Johnson @derricktj
version_added: '2.8'
'''

EXAMPLES = r'''
- name: Configure VLAN
  ucs_vlans:
    hostname: 1.1.1.1
    username: admin
    password: password
    vlangroup: VLANGROUP
    vlanname: VLANNAME
    state: present
- name: Remove VLAN
  ucs_vlans:
    hostname: 1.1.1.1
    username: admin
    password: password
    vlangroup: VLANGROUP
    vlanname: VLANNAME
    state: absent
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec


def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(
        vlangroup=dict(type='str', required=True),
        vlanname=dict(type='str', required=True),
        state=dict(default='present', choices=['present', 'absent'], type='str'),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'present', ['vlangroup', 'vlanname']],
        ],
    )
    ucs = UCSModule(module)

    err = False

    from ucsmsdk.mometa.fabric.FabricNetGroup import FabricNetGroup
    from ucsmsdk.mometa.fabric.FabricPooledVlan import FabricPooledVlan

    
    changed = False
    try:
        mo_exists = False
        props_match = False

        mo = FabricNetGroup(parent_mo_or_dn="fabric/lan", name=module.params['vlangroup'])
        mo_1 = FabricPooledVlan(parent_mo_or_dn=mo, name=module.params['vlanname'])
        
        if mo:
            mo_exists = True

        if module.params['state'] == 'absent':
            if mo_exists:
                if not module.check_mode:
                    ucs.login_handle.remove_mo(mo_1)
                    ucs.login_handle.commit()
                changed = True

        if module.params['state'] == 'present':
            if mo_exists:
                if not module.check_mode:
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
