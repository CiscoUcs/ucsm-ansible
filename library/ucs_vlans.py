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
module: ucs_vlans
short_description: Configures VLANs on Cisco UCS Manager
description:
- Configures VLANs on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify VLANs are present and will create if needed.
    - If C(absent), will verify VLANs are absent and will delete if needed.
    choices: [present, absent]
    default: present
  name:
    description:
    - Name of the VLAN
    - If specifying a single VLAN, name is required
  id:
    description:
    - VLAN ID
    - If specifying a single VLAN, id is required
  native:
    description:
    - native VLAN
    choices: ['no', 'yes']
    default: 'no'
    type: str
  fabric:
    description:
    - Which fabric
    choices: [common, A, B]
    default: common
  multicast_policy:
    description:
    - Multicast Policy Name
  sharing:
    description:
    - Sharing
    choices: [none, primary, isolated, community]
    default: none
  vlan_list:
    description:
    - List of VLANs
    - vlan_list allows multiple resource updates with a single UCSM connection
    - Each list item contains the following properties
    - name (Name of the VLAN pool (required))
    - id (VLAN ID (required))
    - native (native VLAN str specifying 'no' (default) or 'yes')
    - fabric (common (default), A, or B)
    - multicast_policy (Multicast Policy Name)
    - sharing (none (default), primary, isolated, or community)
    - Either vlan_list or name/id is required
requirements:
- ucsmsdk
author:
- David Soper (@dsoper2)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
- name: Configure multiple VLANs
  ucs_vlans:
    hostname: 172.16.143.150
    username: admin
    password: password
    vlan_list:
      - name: vlan100
        id: '100'
      - name: vlan-A-101
        id: '101'
        fabric: A
      - name: vlan-102
        id: '102'
        native: 'yes'
        multicast_policy: default

- name: Configure single VLAN
  ucs_vlans:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: vlan100
    id: '100'
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec


def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(vlan_list=dict(type='list'),
                         name=dict(type='str'),
                         id=dict(type='str'),
                         native=dict(type='str', choices=['no', 'yes']),
                         fabric=dict(type='str', choices=['common', 'A', 'B']),
                         multicast_policy=dict(type='str'),
                         sharing=dict(type='str', choices=['none', 'primary', 'isolated', 'community']),
                         state=dict(type='str', default='present', choices=['present', 'absent']))
    module = AnsibleModule(argument_spec,
                           supports_check_mode=True,
                           required_one_of=[
                               ['vlan_list', 'name']
                           ],
                           mutually_exclusive=[
                               ['vlan_list', 'name']
                           ],
                           required_together=[
                               ['name', 'id']
                           ])
    ucs = UCSModule(module)

    err = False

    from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan

    changed = False
    try:
        if module.params['vlan_list']:
            # directly use the list (single resource and list are mutually exclusive
            vlan_list = module.params['vlan_list']
        else:
            # single resource specified, create list from the current params
            vlan_list = [module.params]
        for vlan in vlan_list:
            exists = False
            # set default params.  Done here to set values for lists which can't be done in the argument_spec
            if not vlan.get('native'):
                vlan['native'] = 'no'
            if not vlan.get('fabric'):
                vlan['fabric'] = 'common'
            if not vlan.get('sharing'):
                vlan['sharing'] = 'none'
            if not vlan.get('multicast_policy'):
                vlan['multicast_policy'] = ''
            # dn is fabric/lan/net-<name> for common vlans or fabric/lan/[A or B]/net-<name> for A or B
            dn_base = 'fabric/lan'
            if vlan['fabric'] != 'common':
                dn_base += '/' + vlan['fabric']
            dn = dn_base + '/net-' + vlan['name']

            mo = ucs.login_handle.query_dn(dn)
            if mo:
                # check top-level mo props
                kwargs = {}
                kwargs['id'] = vlan['id']
                kwargs['default_net'] = vlan['native']
                kwargs['sharing'] = vlan['sharing']
                kwargs['mcast_policy_name'] = vlan['multicast_policy']
                if (mo.check_prop_match(**kwargs)):
                    exists = True

            if module.params['state'] == 'absent':
                if exists:
                    if not module.check_mode:
                        ucs.login_handle.remove_mo(mo)
                        ucs.login_handle.commit()
                    changed = True
            else:
                if not exists:
                    if not module.check_mode:
                        # create if mo does not already exist
                        mo = FabricVlan(parent_mo_or_dn=dn_base,
                                        name=vlan['name'],
                                        id=vlan['id'],
                                        default_net=vlan['native'],
                                        sharing=vlan['sharing'],
                                        mcast_policy_name=vlan['multicast_policy'])

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
