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
module: ucs_service_profile_association
short_description: Configures Service Profile Association on Cisco UCS Manager
description:
- Configures Service Profile Association (change association or disassociate) on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify service profile association and associate with specified server or server pool if needed.
    - If C(absent), will verify service profile is not associated and will disassociate if needed.
    choices: [present, absent]
    default: present
  service_profile_name:
    description:
    - The name of the Service Profile being associated or disassociated.
    required: yes
  association_rn:
    description:
    - The Relative Name (rn) of the association managed object.
    - "For pre-provisioning or selecting an existing server, the Relative Name is 'pn'."
    - "For server pool assignement, the Relative Name is 'pn-req'."
    choices: [pn, pn-req]
    default: pn
  server_dn:
    description:
    - The Distinguished Name (dn) of the server object used for pre-provisioning or selecting an existing server.
    - Required if the association_rn is pn.
    - Optional if the state is absent.
  server_pool_name:
    description:
    - Name of the server pool used for server pool based assignment.
    - Required if the assocation_rn is pn-req.
    - Optional if the state is absent.
  restrict_migration:
    description:
    - Restricts the migration of the service profile after it has been associated with a server.
    - If set to no, Cisco UCS Manager does not perform any compatibility checks on the new server before migrating the existing service profile.
    - If set to no and the hardware of both servers used in migration are not similar, the association might fail.
    choices: ['yes', 'no']
    default: 'no'
  org_dn:
    description:
    - The distinguished name (dn) of the organization where the resource is assigned.
    default: org-root
requirements:
- ucsmsdk
author:
- David Soper (@dsoper2)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
- name: Change Service Profile Association to server pool Container-Pool and restrict migration
  ucs_service_profile_association:
    hostname: 172.16.143.150
    username: admin
    password: password
    service_profile_name: test-sp
    association_rn: pn-req
    server_pool_name: Container-Pool
    restrict_migration: 'yes'

- name: Attempt to change association once a minute for up to 10 minutes
  ucs_service_profile_association:
    hostname: 172.16.143.150
    username: admin
    password: password
    service_profile_name: test-sp
    server_dn: sys/chassis-2/blade-1
  register: result
  until: result.assign_state == 'assigned' and result.assoc_state == 'associated'
  retries: 10
  delay: 60

- name: Disassociate Service Profile
  ucs_service_profile_association:
    hostname: 172.16.143.150
    username: admin
    password: password
    service_profile_name: test-sp
    state: absent
'''

RETURN = r'''
assign_state:
  description: The logical server Assigned State (assigned, unassigned, or failed).
  returned: success
  type: string
  sample: assigned
assoc_state:
  description: The logical server Association State (associated or unassociated).
  returned: success
  type: string
  sample: associated
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec


def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(
        org_dn=dict(type='str', default='org-root'),
        service_profile_name=dict(type='str', required=True),
        association_rn=dict(type='str', default='pn', choices=['pn', 'pn-req']),
        server_dn=dict(type='str'),
        server_pool_name=dict(type='str'),
        restrict_migration=dict(type='str', default='no', choices=['yes', 'no']),
        state=dict(default='present', choices=['present', 'absent'], type='str'),
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ['server_dn', 'server_pool_name'],
        ],
    )
    # UCSModule verifies ucsmsdk is present and exits on failure.  Imports are below ucs object creation.
    ucs = UCSModule(module)

    err = False

    from ucsmsdk.mometa.ls.LsRequirement import LsRequirement
    from ucsmsdk.mometa.ls.LsBinding import LsBinding

    changed = False
    ucs.result['assign_state'] = 'unassigned'
    ucs.result['assoc_state'] = 'unassociated'
    try:
        ls_mo_exists = False
        pn_mo_exists = False
        props_match = False

        # logical server distinguished name is <org>/ls-<name> and physical node dn appends 'pn' or 'pn-req'
        ls_dn = module.params['org_dn'] + '/ls-' + module.params['service_profile_name']
        ls_mo = ucs.login_handle.query_dn(ls_dn)
        if ls_mo:
            ls_mo_exists = True

        if module.params['state'] == 'absent':
            if ls_mo_exists and ls_mo.assign_state != 'unassigned':
                # query pn then pn-req to find server association
                pn_dn = ls_dn + '/pn'
                pn_mo = ucs.login_handle.query_dn(pn_dn)
                if pn_mo:
                    pn_mo_exists = True
                else:
                    pn_dn = ls_dn + '/pn-req'
                    pn_mo = ucs.login_handle.query_dn(pn_dn)
                    if pn_mo:
                        pn_mo_exists = True

            if pn_mo_exists:
                if not module.check_mode:
                    ucs.login_handle.remove_mo(pn_mo)
                    ucs.login_handle.commit()
                changed = True
        else:
            if ls_mo_exists:
                # verify logical server is assigned and associated
                # when server slots are being pre-provisioned (assigned is false), this module always tries to change state
                ucs.result['assign_state'] = ls_mo.assign_state
                ucs.result['assoc_state'] = ls_mo.assoc_state
                if ls_mo.assign_state == 'assigned' and ls_mo.assoc_state == 'associated':
                    props_match = True

            if not props_match:
                if not module.check_mode:
                    # create if mo does not already exist in desired state
                    if module.params.get('server_dn'):
                        mo = LsBinding(
                            parent_mo_or_dn=ls_dn,
                            pn_dn=module.params['server_dn'],
                            restrict_migration=module.params['restrict_migration'],
                        )
                    else:
                        mo = LsRequirement(
                            parent_mo_or_dn=ls_dn,
                            name=module.params['server_pool_name'],
                            restrict_migration=module.params['restrict_migration'],
                        )

                    ucs.login_handle.add_mo(mo, True)
                    ucs.login_handle.commit()
                    ls_mo = ucs.login_handle.query_dn(ls_dn)
                    if ls_mo:
                        ucs.result['assign_state'] = ls_mo.assign_state
                        ucs.result['assoc_state'] = ls_mo.assoc_state
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
