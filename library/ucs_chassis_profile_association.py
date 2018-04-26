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
module: ucs_chassis_profile_association
short_description: Configures Chassis Profile Association on Cisco UCS Manager
description:
- Configures Chassis Profile Association (change association or disassociate) on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify chassis profile association and associate with specified chassis if needed.
    - If C(absent), will verify chassis profile is not associated and will disassociate if needed.  This is the same as specifying Assign Later in the webUI.
    choices: [present, absent]
    default: present
  chassis_profile_name:
    description:
    - The name of the Chassis Profile being associated or disassociated.
    required: yes
  chassis_dn:
    description:
    - The Distinguished Name (dn) of the chassis object used for pre-provisioning or selecting an existing chassis.
    - Required if the chassis_assignment option is chassis.
    - Optional if the state is absent.
  restrict_migration:
    description:
    - Restricts the migration of the chassis profile after it has been associated with a chassis.
    - If set to no, Cisco UCS Manager does not perform any compatibility checks on the new chassis before migrating the existing chassis profile.
    - If set to no and the hardware of both chassis used in migration are not similar, the association might fail.
    choices: ['yes', 'no']
    default: 'no'
requirements:
- ucsmsdk
author:
- Olli Walsdorf (@owalsdor)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
- name: Change Chassis Profile Association and restrict migration
  ucs_chassis_profile_association:
    hostname: 172.16.143.150
    username: admin
    password: password
    chassis_profile_name: S3260_1
    chassis_dn: sys/chassis-1
    restrict_migration: 'yes'

- name: Disassociate Chassis Profile
  ucs_service_profile_association:
    hostname: 172.16.143.150
    username: admin
    password: password
    chassis_profile_name: S3260_1
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
        chassis_profile_name=dict(type='str', required=True),
        chassis_dn=dict(type='str'),
        restrict_migration=dict(type='str', default='no', choices=['yes', 'no']),
        state=dict(default='present', choices=['present', 'absent'], type='str'),
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )
    ucs = UCSModule(module)

    err = False

    # UCSModule verifies ucsmsdk is present and exits on failure.  Imports are below ucs object creation.
    from ucsmsdk.mometa.equipment.EquipmentBinding import EquipmentBinding

    changed = False
    ucs.result['assign_state'] = 'unassigned'
    ucs.result['assoc_state'] = 'unassociated'
    try:
        cp_mo_exists = False
        assoc_mo_exists = False
        props_match = False

        # logical chassis distinguished name is <org>/cp-<name>
        cp_dn = module.params['org_dn'] + '/cp-' + module.params['chassis_profile_name']
        cp_mo = ucs.login_handle.query_dn(cp_dn)
        if cp_mo:
            cp_mo_exists = True
            assoc_mo_dn = cp_dn + '/chassis'
            assoc_mo = ucs.login_handle.query_dn(assoc_mo_dn)
            if assoc_mo:
                assoc_mo_exists = True

        if module.params['state'] == 'absent':
            if cp_mo_exists and cp_mo.assign_state != 'unassigned' and assoc_mo_exists:
                if not module.check_mode:
                    ucs.login_handle.remove_mo(assoc_mo)
                    ucs.login_handle.add_mo(cp_mo, True)
                    ucs.login_handle.commit()
                changed = True

        else:
            if cp_mo_exists:
                ucs.result['assign_state'] = cp_mo.assign_state
                ucs.result['assoc_state'] = cp_mo.assoc_state
                if assoc_mo_exists:
                    # check the current chassis association
                    kwargs = dict(chassis_dn=module.params['chassis_dn'])
                    if assoc_mo.check_prop_match(**kwargs):
                        props_match = True

            if not props_match:
                if not module.check_mode:
                    mo = EquipmentBinding(
                        parent_mo_or_dn=cp_dn,
                        chassis_dn=module.params['chassis_dn'],
                        restrict_migration=module.params['restrict_migration'],
                    )

                    ucs.login_handle.add_mo(mo, True)
                    ucs.login_handle.commit()
                    cp_mo = ucs.login_handle.query_dn(cp_dn)
                    if cp_mo:
                        ucs.result['assign_state'] = cp_mo.assign_state
                        ucs.result['assoc_state'] = cp_mo.assoc_state
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
