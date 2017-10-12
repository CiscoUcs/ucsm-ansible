#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: ucs_bios_policy
short_description: Configures BIOS policies on Cisco UCS Manager
description:
- Configures BIOS policies on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify BIOS policy is present and will create if needed.
    - If C(absent), will verify BIOS policy is absent and will delete if needed.
    choices: [present, absent]
    default: present
  name:
    description:
    - BIOS policy name
    required: yes
  descr:
    description:
    - BIOS policy description
  reboot_on_update:
    description:
    - Reboot on BIOS settings change
    default: 'no'
  resume_on_power_loss:
    description:
    - Resume on AC power loss
    default: platform-default
  cdn_control:
    description:
    - CDN (Consistent Device Naming) control
    default: disabled
  org_dn:
    description:
    - Org dn (distinguished name)
    default: org-root
requirements:
- ucsmsdk
author:
- David Soper (@dsoper2)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
- name: Configure BIOS policy
  ucs_bios_policy:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: CDN Enabled
    descr: Enable CDN
    cdn_control: enabled
    resume_on_power_loss: last-state
    reboot_on_update: 'yes'
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ucs import UcsConnection, ucs_argument_spec


def _argument_mo():
    return dict(
        name=dict(required=True, type='str'),
        org_dn=dict(type='str', default='org-root'),
        descr=dict(required=False, type='str', default=''),
        reboot_on_update=dict(required=False,
                              choices=['yes', 'no'],
                              type='str', default='no'),
        resume_on_power_loss=dict(required=False,
                                  choices=['last-state', 'platform-default'],
                                  type='str', default='platform-default'),
        cdn_control=dict(required=False,
                         choices=['enabled', 'disabled'],
                         type='str', default='disabled')
    )


def _argument_custom():
    return dict(
        state=dict(default='present',
                   choices=['present', 'absent'],
                   type='str')
    )


def _argument_connection():
    return dict(
        # UcsHandle
        login_handle=dict(type='dict'),
    )


def _ansible_module_create():
    argument_spec = ucs_argument_spec
    argument_spec.update(_argument_mo())
    argument_spec.update(_argument_custom())
    argument_spec.update(_argument_connection())

    return AnsibleModule(argument_spec,
                         supports_check_mode=True)


def _get_mo_params(params):
    args = {}
    for key in _argument_mo():
        if params.get(key) is None:
            continue
        args[key] = params.get(key)
    return args


def setup_bios_policy(login_handle, module):
    from ucsmsdk.mometa.bios.BiosVProfile import BiosVProfile
    from ucsmsdk.mometa.bios.BiosVfConsistentDeviceNameControl import BiosVfConsistentDeviceNameControl
    from ucsmsdk.mometa.bios.BiosVfFrontPanelLockout import BiosVfFrontPanelLockout
    from ucsmsdk.mometa.bios.BiosVfPOSTErrorPause import BiosVfPOSTErrorPause
    from ucsmsdk.mometa.bios.BiosVfQuietBoot import BiosVfQuietBoot
    from ucsmsdk.mometa.bios.BiosVfResumeOnACPowerLoss import BiosVfResumeOnACPowerLoss

    ansible = module.params
    args_mo = _get_mo_params(ansible)

    changed = False

    exists = False
    dn = args_mo['org_dn'] + '/bios-prof-' + args_mo['name']
    mo = login_handle.query_dn(dn)
    if mo:
        exists = True

    if ansible['state'] == 'absent':
        if exists:
            changed = True
            if not module.check_mode:
                login_handle.remove_mo(mo)
                login_handle.commit()
    else:
        if not exists:
            changed = True
            if not module.check_mode:
                if 'reboot_on_update' not in args_mo:
                    args_mo['reboot_on_update'] = 'no'
                mo = BiosVProfile(
                    parent_mo_or_dn=args_mo['org_dn'],
                    name=args_mo['name'],
                    reboot_on_update=args_mo['reboot_on_update'],
                    descr=args_mo['descr'])

                if 'reboot_on_power_loss' in args_mo:
                    m_1 = BiosVfResumeOnACPowerLoss(parent_mo_or_dn=mo, vp_resume_on_ac_power_loss=args_mo['reboot_on_power_loss'])
                # consistent device naming
                if 'cdn_control' in args_mo:
                    mo_2 = BiosVfConsistentDeviceNameControl(parent_mo_or_dn=mo, vp_cdn_control=args_mo['cdn_control'])

                login_handle.add_mo(mo, True)
                login_handle.commit()

    return changed


def setup(login_handle, module):
    result = {}
    err = False

    try:
        result['changed'] = setup_bios_policy(login_handle, module)
    except Exception as e:
        err = True
        result['msg'] = "setup error: %s " % str(e)
        result['changed'] = False

    return result, err


def main():
    module = _ansible_module_create()
    conn = UcsConnection(module)
    login_handle = conn.login()
    result, err = setup(login_handle, module)
    conn.logout()
    if err:
        module.fail_json(**result)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
