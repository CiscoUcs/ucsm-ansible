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
  vlan_list:
    description:
    - List of VLANs which contain the following properties
    - name (Name of the VLAN pool (required))
    - id (VLAN ID (required))
    - native (native VLAN str specifying no (default) or yes)
    - sharing (none (default), primary, isolated, or community)
    - multicast_policy (Multicast Policy Name)
    - fabric (common (default), A, or B)
    required: yes
requirements:
- ucsmsdk
author:
- David Soper (@dsoper2)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
- name: Configure MAC address pool
  ucs_vlans:
    hostname: 172.16.143.150
    username: admin
    password: password
    vlan_list:
      - name: vlan101
        id: '100'
      - name: vlan-A-101
        id: '101'
        fabric: A
      - name: vlan-102
        id: '102'
        native: 'yes'
        multicast_policy: default
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec


def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(vlan_list=dict(required=True, type='list'),
                         state=dict(default='present', choices=['present', 'absent'], type='str'))
    module = AnsibleModule(argument_spec,
                           supports_check_mode=True)
    ucs = UCSModule(module)

    err = False

    from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan

    changed = False
    try:
        for vlan in module.params['vlan_list']:
            exists = False
            dn_base = 'fabric/lan'
            if 'fabric' in vlan:
                dn_base += '/' + vlan['fabric']
            dn = dn_base + '/net-' + vlan['name']
            mo = ucs.login_handle.query_dn(dn)
            if mo:
                # check top-level mo props
                kwargs = {}
                kwargs['id'] = vlan['id']
                if 'native' not in vlan:
                    vlan['native'] = 'no'
                kwargs['default_net'] = vlan['native']
                if 'sharing' not in vlan:
                    vlan['sharing'] = 'none'
                kwargs['sharing'] = vlan['sharing']
                if 'multicast_policy' not in vlan:
                    vlan['multicast_policy'] = ''
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
