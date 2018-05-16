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
module: ucs_chassis_profile_from_template
short_description: Configures Chassis Profiles from templates on Cisco UCS Manager
description:
- Configures Chassis Profile created from templates on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify Chassis Profiles are present and will create if needed.
    - If C(absent), will verify Chassis Profiles are absent and will delete if needed.
    choices: [present, absent]
    default: present
  name:
    description:
    - The name of the chassis profile.
    - This name can be between 2 and 32 alphanumeric characters.
    - "You cannot use spaces or any special characters other than - (hyphen), \"_\" (underscore), : (colon), and . (period)."
    - This name must be unique across all chassis profiles and chassis profile templates within the same organization.
    required: yes
  description:
    description:
    - A user-defined description of the chassis profile template.
    - Enter up to 256 characters.
    - "You can use any characters or spaces except the following:"
    - "` (accent mark), \ (backslash), ^ (carat), \" (double quote), = (equal sign), > (greater than), < (less than), or ' (single quote)."
    aliases: [ descr ]
  source_template:
    description:
    - The name of the chassis profile template used to create this chassis profile.
    required: yes
requirements:
- ucsmsdk
author:
- Olli Walsdorf (@owalsdor)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
- name: Configure Chassis Profile from Template
  ucs_chassis_profile_from_template:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: S3260_1
    source_template: S3260_Template

- name: Remove Chassis Profile
  ucs_chassis_profile_from_template:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: S3260_1
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
        org_dn=dict(type='str', default='org-root'),
        name=dict(type='str', required=True),
        description=dict(type='str', default=''),
        source_template=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )
    ucs = UCSModule(module)

    err = False

    # UCSModule creation above verifies ucsmsdk is present and exits on failure.  Additional imports are done below.
    from ucsmsdk.mometa.equipment.EquipmentChassisProfile import EquipmentChassisProfile

    changed = False
    try:
        mo_exists = False
        props_match = False
        dn_base = 'org-root'
        dn = dn_base + '/cp-' + module.params['name']

        mo = ucs.login_handle.query_dn(dn)
        if mo:
            mo_exists = True

        if module.params['state'] == 'absent':
            # mo must exist but all properties do not have to match
            if mo_exists:
                if not module.check_mode:
                    ucs.login_handle.remove_mo(mo)
                    ucs.login_handle.commit()
                changed = True
        else:
            if mo_exists:
                # check top-level mo props
                kwargs = dict(src_templ_name=module.params['source_template'])
                kwargs['descr'] = module.params['description']
                # chassis profiles are of type 'instance'
                kwargs['type'] = 'instance'
                if mo.check_prop_match(**kwargs):
                    props_match = True

            if not props_match:
                if not module.check_mode:
                    # create if mo does not already exist
                    mo = EquipmentChassisProfile(
                        parent_mo_or_dn=dn_base,
                        name=module.params['name'],
                        descr=module.params['description'],
                        src_templ_name=module.params['source_template'],
                        type='instance',
                    )

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
