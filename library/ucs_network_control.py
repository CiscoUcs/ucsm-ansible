#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: ucs_network_control
short_description: Confgures network control policies on Cisco UCS Manager
description:
- Configures Confgures network control policies on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify network control policies are present and will create if needed.
    - If C(absent), will verify network control policies are absent and will delete if needed.
    choices: [present, absent]
    default: present
  name:
    description:
    - The name assigned to the Network .
    - The network control policies name is case sensitive.
    - This name can be between 1 and 32 alphanumeric characters.
    - "You cannot use spaces or any special characters other than - (hyphen), \"_\" (underscore), : (colon), and . (period)."
    - You cannot change this name after the network control policies is created.
    required: yes
  descrption:
    description:
    - The user-defined description of the network control policy.
    aliases: [ descr ]
  cdp:
    description:
    - "Set state of CDP"
    - "disabled - disables CDP"
    - "enabled - enables CDP"
    choices: [disabled, enabled]
    default: 'disabled'
  mac_register_mode:
    description:
    - "Configure which VLAN the vNIC MAC address registers on:"
    - "all-host-vlans - Register MAC address on all VLANs."
    - "only-native-vlan — Register MAC address on only the native VLAN."
    choices: [all-host-vlans, only-native-vlan]
    default: 'only-native-vlan'
  uplink_fail_action:
    description:
    - "Action to talk when link fails:"
    - "link-down — Place vNIC in a down state."
    - "warning - Only issue a warning."
    choices: [link-down, warning]
    default: 'link-down'
  forge:
    description:
    - "Allow or deny forged transmits:"
    - "allow - Allow forged transmits."
    - "deny — Deny forged transmits."
    - "no-config - Do not configure this setting, use with UCS Mini"
    choices: [allow, deny, no-config]
    default: 'deny'
  lldp_transmit:
    description:
    - "Enable or disable LLDP transmission:"
    - "enabled - Enable LLDP Transmission."
    - "disabled — Disable LLDP Transmission."
    choices: [enabled, disabled]
    default: 'disabled'
  lldp_receive:
    description:
    - "Enable or disable receiving of LLDP transmissions:"
    - "enabled - Enable receiving of LLDP transmissions."
    - "disabled — Disable receiving of LLDP transmissions."
    choices: [enabled, disabled]
    default: 'disabled'
  org_dn:
    description:
    - Org dn (distinguished name)
    default: org-root

requirements:
- ucsmsdk
author:
- Brett Johnson (@sdbrett)
'''

EXAMPLES = r'''
- name: Configure network control policies
  ucs_network_control:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: enable_cdp
    cdp: enable

- name: Remove network control policies
  control policies:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: enable_cdp
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
        descr=dict(type='str', default=''),
        cdp=dict(type='str', default='disabled'),
        mac_register_mode=dict(type='str', default='only-native-vlan', choices=['all-host-vlan', 'only-native-vlan']),
        uplink_fail_action=dict(type='str', default='link-down', choices=['link-down', 'warning']),
        forge=dict(type='str', default='deny', choices=['allow', 'deny', 'no-config']),
        lldp_transmit=dict(type='str', default='disabled', choices=['disabled', 'enabled']),
        lldp_receive=dict(type='str', default='disabled', choices=['disabled', 'enabled']),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )
    ucs = UCSModule(module)

    err = False

    # UCSModule creation above verifies ucsmsdk is present and exits on failure, so additional imports are done below.
    from ucsmsdk.mometa.nwctrl.NwctrlDefinition import NwctrlDefinition
    from ucsmsdk.mometa.dpsec.DpsecMac import DpsecMac

    changed = False
    try:
        mo_exists = False
        props_match = False
        # dn is fabric/lan/net-<name> for common network control policies or fabric/lan/[A or B]/net-<name> for A or B
        dn = module.params['org_dn'] + '/nwctrl-' + module.params['name']

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
                kwargs = dict(name=module.params['name'])
                kwargs['cdp'] = module.params['cdp']
                kwargs['descr'] = module.params['descr']
                kwargs['mac_register_mode'] = module.params['mac_register_mode']
                kwargs['uplink_fail_action'] = module.params['uplink_fail_action']
                kwargs['lldp_receive'] = module.params['lldp_receive']
                kwargs['lldp_transmit'] = module.params['lldp_transmit']
                if mo.check_prop_match(**kwargs):
                    props_match = True

            if not props_match:
                if not module.check_mode:
                    # create if mo does not already exist
                    mo = NwctrlDefinition(parent_mo_or_dn=module.params['org_dn'],
                                          lldp_transmit=module.params['lldp_transmit'],
                                          name=module.params['name'],
                                          lldp_receive=module.params['lldp_receive'],
                                          mac_register_mode=module.params['mac_register_mode'],
                                          policy_owner="local",
                                          cdp=module.params['cdp'],
                                          uplink_fail_action=module.params['uplink_fail_action'],
                                          descr=module.params['descr'])
                    if not module.params['forge'] == 'no-config':
                        DpsecMac(parent_mo_or_dn=mo,
                                 forge=module.params['forge'],
                                 policy_owner="local",
                                 name="",
                                 descr="")

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
