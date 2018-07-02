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
module: ucs_sp_vnic_order

short_description: Configures vNIC order for service profiles and templates on Cisco UCS Manager

version_added: "2.6"

description:
    - Configures Configures vNIC order for service profiles and templates on Cisco UCS Manager
    - Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).

options:
    sp_name:
        description: DN of the service profile
    - vnics:
        description: List of vNIC order properties
        name:
            description: Name of the vNIC
        admin_vcon:
            description: Name of the virtual connection
            choices: ["1",2","3","4","any"]
        order:
            description: vNIC connection order
            choices: ["unspecified", "0-256"]
        transport:
            description: transport medium
            choices: ["ethernet", "fc"]
    org_dn:
        description: root org dn
extends_documentation_fragment:
    - ucs
requirements:
    - ucsmsdk
author:
    - Brett Johnson (@sdbrett)

'''

EXAMPLES = r'''
- name: Configure vnic order
  ucs_sp_vnic_order:
    sp_name: my_sp
    vnics:
    - name: 'my_vnic'
      admin_vcon: '1'
      order: '1'
      transport: 'ethernet'
    hostname: 192.168.99.100
    username: admin
    password: password
- name: Configure vhba order
  ucs_sp_vnic_order:
    sp_name: my_sp
    vnics:
    - name: 'my_vhba'
      admin_vcon: '2'
      order: '1'
      transport: 'fc'
    hostname: 192.168.99.100
    username: admin
    password: password
- name: Configure vnic and vhba order
  ucs_sp_vnic_order:
    sp_name: my_sp
    vnics:
    - name: my_vhba
      admin_vcon: '2'
      order: '1'
      transport: fc
    - name: my_vnic
      admin_vcon: '1'
      order: '1'
      transport: ethernet
    hostname: 192.168.99.100
    username: admin
    password: password
- name: Remove vnic order configuration from my_vnic
  ucs_sp_vnic_order:
    sp_name: my_sp
    vnics:
    - name: 'my_vnic'
      transport: ethernet
      state: absent
    hostname: 192.168.99.100
    username: admin
    password: password

'''

RETURN = r'''
#
'''


def get_service_profile(handle, org_dn, sp_name):
    dn = org_dn + "/ls-" + sp_name
    sp = handle.query_dn(dn)
    return sp


def update_vnic_assignment_order(ucs, vnic, sp):
    from ucsmsdk.mometa.ls.LsVConAssign import LsVConAssign

    mo = LsVConAssign(parent_mo_or_dn=sp, admin_vcon=vnic['admin_vcon'],
                      order=vnic['order'], transport=vnic['transport'],
                      vnic_name=vnic['name'])
    ucs.login_handle.add_mo(mo, True)
    ucs.login_handle.commit()


def remove_vnic_assignment_order(ucs, vnic, sp):
    from ucsmsdk.mometa.ls.LsVConAssign import LsVConAssign

    mo = LsVConAssign(parent_mo_or_dn=sp, admin_vcon='any',
                      order='unspecified', transport=vnic['transport'],
                      vnic_name=vnic['name'])
    ucs.login_handle.add_mo(mo, True)
    ucs.login_handle.commit()


def get_vnic(ucs, dn):
    return ucs.login_handle.query_dn(dn)


def get_vnic_dn(sp_dn, transport, name):
    if transport == 'ethernet':
        return sp_dn + '/ether-' + name
    return sp_dn + '/fc-' + name


def matches_existing_vnic_order(vnic, vnic_mo):
    if vnic['state'] == 'absent':
        kwargs = dict(admin_vcon='any')
        kwargs['order'] = 'unspecified'
    else:
        kwargs = dict(admin_vcon=vnic['admin_vcon'])
        kwargs['order'] = vnic['order']

    if vnic['transport'] == 'ethernet':
        kwargs['type'] = 'ether'
    else:
        kwargs['type'] = vnic['transport']
    return vnic_mo.check_prop_match(**kwargs)


def main():
    from ansible.module_utils.basic import AnsibleModule
    from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec
    argument_spec = ucs_argument_spec
    argument_spec.update(
        sp_name=dict(required=True, type='str'),
        vnics=dict(required=True, type='list'),
        org_dn=dict(required=False, type='str', default='org-root'),
    )
    module = AnsibleModule(argument_spec,
                           supports_check_mode=True)
    ucs = UCSModule(module)

    err = False
    changed = False

    try:
        sp_dn = dn = module.params['org_dn'] + "/ls-" + module.params['sp_name']
        sp = ucs.login_handle.query_dn(dn)
        if not sp:
            raise ValueError("SP '%s' does not exist" % sp_dn)

        for vnic in module.params['vnics']:
            vnic_mo = get_vnic(ucs, (get_vnic_dn(sp_dn, vnic['transport'], vnic['name'])))

            if vnic['state'] != 'absent' and not vnic_mo:
                raise ValueError("vNIC '%s' is not assigned to service profile '%s'" % (vnic['name'], sp_dn))

            if vnic_mo:
                if not matches_existing_vnic_order(vnic, vnic_mo):
                    changed = True
                    break

        if changed and not module.check_mode:
            for vnic in module.params['vnics']:
                vnic_mo = get_vnic(ucs, (get_vnic_dn(sp_dn, vnic['transport'], vnic['name'])))
                if vnic['state'] == 'absent' and vnic_mo:
                    remove_vnic_assignment_order(ucs, vnic, sp)
                elif not vnic_mo:

                    update_vnic_assignment_order(ucs, vnic, sp)
                elif not matches_existing_vnic_order(vnic, vnic_mo):
                    update_vnic_assignment_order(ucs, vnic, sp)

    except Exception as e:
        err = True
        ucs.result['msg'] = "setup error: %s " % str(e)

    ucs.result['changed'] = changed
    if err:
        module.fail_json(**ucs.result)
    module.exit_json(**ucs.result)


if __name__ == '__main__':
    main()
