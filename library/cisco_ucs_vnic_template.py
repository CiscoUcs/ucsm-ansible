#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: ucs_vnic_template
short_description: Configures vNIC templates on Cisco UCS Manager
description:
- Configures vNIC templates on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify vNIC template is present and will create if needed.
    - If C(absent), will verify vNIC template is absent and will delete if needed.
    choices: [present, absent]
    default: present
  vnic_list:
    description:
    - List of vNIC templates specifying the name of the template, fabric ID,
      and policies used by the template.
    required: yes
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
- name: Configure vNIC template
  ucs_vnic_template:
    hostname: 172.16.143.150
    username: admin
    password: password
    vnic_list:
      - name: test-eth0
        side: A
        vlans:
        - name: default
          native: 'yes'
        cdn_name: eth0
        mtu: '1500'
        mac_pool: mac-A
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ucs import UcsConnection, ucs_argument_spec


def _argument_mo():
    return dict(
        vnic_list=dict(required=True, type='list'),
        org_dn=dict(type='str', default='org-root'),
    )


def _argument_custom():
    return dict(
        state=dict(default='present',
                   choices=['present', 'absent'],
                   type='str'),
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


def update_nic(login_handle, vnic, org):
    from ucsmsdk.mometa.vnic.VnicLanConnTempl import VnicLanConnTempl
    from ucsmsdk.mometa.vnic.VnicEtherIf import VnicEtherIf
    # create if mo does not already exist
    if 'description' not in vnic:
        vnic['description'] = ''
    if 'qos_policy' not in vnic:
        vnic['qos_policy'] = ''
    if 'mtu' not in vnic:
        vnic['mtu'] = '1500'
    if 'stats_policy' not in vnic:
        vnic['stats_policy'] = 'default'

    # default template is updating, this is different than
    # standard UCS because UCS made the wrong decision for
    # default.
    if 'updating' in vnic:
        if vnic['updating'] == 'yes':
            vnic['updating'] = 'updating-template'
        else:
            vnic['updating'] = 'initial-template'
    else:
        vnic['updating'] = 'updating-template'

    if 'nw_ctrl_policy' not in vnic:
        vnic['nw_ctrl_policy'] = ''
    mo = VnicLanConnTempl(parent_mo_or_dn=org,
                          templ_type=vnic['updating'],
                          descr=vnic['description'],
                          ident_pool_name=vnic['mac_pool'],
                          name=vnic['name'],
                          mtu=vnic['mtu'],
                          qos_policy_name=vnic['qos_policy'],
                          stats_policy_name=vnic['stats_policy'],
                          nw_ctrl_policy_name=vnic['nw_ctrl_policy'],
                          switch_id=vnic['side'])

    if 'vlans' in vnic:
        for v in vnic['vlans']:
            if 'native' not in v:
                v['native'] = 'no'
            mo_x = VnicEtherIf(parent_mo_or_dn=mo,
                               default_net=v['native'],
                               name=v['name'])

    login_handle.add_mo(mo, True)
    login_handle.commit()


def check_templ(mo, vnic):
    if 'updating' in vnic:
        if vnic['updating'] == 'yes' and mo.templ_type == 'updating-template':
            # no change.
            return False
        elif vnic['updating'] == 'no' and mo.templ_type == 'initial-template':
            # no change.
            return False

    if not mo.templ_type == 'updating-template':
        return False

    return False


# compares existing VNIC template to see if something changed.
def did_change(mo, vnic):
    # go through each part.
    if mo.switch_id != vnic['side']:
        return True
    if 'mtu' in vnic:
        if mo.mtu != vnic['mtu']:
            return True
    else:
        if mo.mtu != '1500':
            return True

    if mo.ident_pool_name != vnic['mac_pool']:
        return True

    return False


def setup_vnic_template(login_handle, module):
    from ucsmsdk.mometa.vnic.VnicLanConnTempl import VnicLanConnTempl
    from ucsmsdk.mometa.vnic.VnicEtherIf import VnicEtherIf

    ansible = module.params
    args_mo = _get_mo_params(ansible)

    changed = False

    for vnic in args_mo['vnic_list']:
        exists = False
        dn = args_mo['org_dn'] + '/lan-conn-templ-' + vnic['name']
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
                    update_nic(login_handle, vnic, args_mo['org_dn'])
            else:
                ch = did_change(mo, vnic)
                if ch:
                    changed = True
                    if not module.check_mode:
                        update_nic(login_handle, vnic, args_mo['org_dn'])

    return changed


def setup(login_handle, module):
    result = {}
    err = False

    try:
        result['changed'] = setup_vnic_template(login_handle, module)
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
