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
module: ucs_ippool
short_description: Configures IP address pools on Cisco UCS Manager
description:
- Configures IP address pools and IP pool blocks on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify IP pool is present and will create if needed.
    - If C(absent), will verify IP pool is absent and will delete if needed.
    choices: [present, absent]
    default: present
  ip_list:
    description:
    - List of IP pools which contain the following properties
    - name (Name of the IP pool (required))
    - descr (Description for the IP pool)
    - order (Assignment order, default or sequential)
    - first_addr (First IPv4 address in the IP addresses block)
    - last_addr (Last IPv4 address in the IP addresses block)
    - subnet_mask (IPv4 Subnet Mask)
    - default_gw (IPv4 Default Gateway)
    - primary_dns (IPv4 Primary DNS)
    - secondary_dns (IPv4 Secondary DNS)
    - ipv6_first_addr (First IPv6 address in the IP addresses block)
    - ipv6_last_addr (Last IPv6 address in the IP addresses block)
    - ipv6_prefix (IPv6 address prefix)
    - ipv6_default_gw (IPv6 Default Gateway)
    - ipv6_primary_dns (IPv6 Primary DNS)
    - ipv6_secondary_dns (IPv6 Secondary DNS)
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
- name: Configure IP address pool
  ucs_ippool:
    hostname: 172.16.143.150
    username: admin
    password: password
    ip_list:
      - name: ip-A
        order: sequential
        first_addr: 192.168.0.10
        last_addr: 192.168.0.19
        subnet_mask: 255.255.255.0
        default_gw: 192.168.0.1
        primary_dns: 172.16.143.136
      - name: ipv6-B
        ipv6_first_addr: fe80::1cae:7992:d7a1:edfe
        ipv6_last_addr: fe80::1cae:7992:d7a1:ed07
        ipv6_default_gw: fe80::1cae:7992:d7a1:ecff
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec


def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(ip_list=dict(required=True, type='list'),
                         org_dn=dict(type='str', default='org-root'),
                         state=dict(default='present', choices=['present', 'absent'], type='str'))
    module = AnsibleModule(argument_spec,
                           supports_check_mode=True)
    ucs = UCSModule(module)

    err = False

    from ucsmsdk.mometa.ippool.IppoolPool import IppoolPool
    from ucsmsdk.mometa.ippool.IppoolBlock import IppoolBlock
    from ucsmsdk.mometa.ippool.IppoolIpV6Block import IppoolIpV6Block

    changed = False
    try:
        for ip in module.params['ip_list']:
            exists = False
            dn = module.params['org_dn'] + '/ip-pool-' + ip['name']
            # set default params
            if 'order' not in ip:
                ip['order'] = 'default'
            if 'descr' not in ip:
                ip['descr'] = ''
            if 'subnet_mask' not in ip:
                ip['subnet_mask'] = '255.255.255.0'
            if 'default_gw' not in ip:
                ip['default_gw'] = '0.0.0.0'
            if 'primary_dns' not in ip:
                ip['primary_dns'] = '0.0.0.0'
            if 'secondary_dns' not in ip:
                ip['secondary_dns'] = '0.0.0.0'
            if 'ipv6_prefix' not in ip:
                ip['ipv6_prefix'] = '64'
            if 'ipv6_default_gw' not in ip:
                ip['ipv6_default_gw'] = '::'
            if 'ipv6_primary_dns' not in ip:
                ip['ipv6_primary_dns'] = '::'
            if 'ipv6_secondary_dns' not in ip:
                ip['ipv6_secondary_dns'] = '::'

            mo = ucs.login_handle.query_dn(dn)
            if mo:
                # check top-level mo props
                kwargs = {}
                kwargs['assignment_order'] = ip['order']
                kwargs['descr'] = ip['descr']
                if (mo.check_prop_match(**kwargs)):
                    # top-level props match, check next level mo/props
                    exists = True
                    if 'last_addr' in ip and 'first_addr' in ip:
                        block_dn = dn + '/block-' + ip['first_addr'] + '-' + ip['last_addr']
                        mo_1 = ucs.login_handle.query_dn(block_dn)
                        if mo_1:
                            kwargs = {}
                            kwargs['subnet'] = ip['subnet_mask']
                            kwargs['def_gw'] = ip['default_gw']
                            kwargs['prim_dns'] = ip['primary_dns']
                            kwargs['sec_dns'] = ip['secondary_dns']
                            if (not mo_1.check_prop_match(**kwargs)):
                                exists = False
                        else:
                            exists = False

                    if 'ipv6_last_addr' in ip and 'ipv6_first_addr' in ip:
                        block_dn = dn + '/v6block-' + ip['ipv6_first_addr'].lower() + '-' + ip['ipv6_last_addr'].lower()
                        mo_1 = ucs.login_handle.query_dn(block_dn)
                        if mo_1:
                            kwargs = {}
                            kwargs['prefix'] = ip['ipv6_prefix']
                            kwargs['def_gw'] = ip['ipv6_default_gw']
                            kwargs['prim_dns'] = ip['ipv6_primary_dns']
                            kwargs['sec_dns'] = ip['ipv6_secondary_dns']
                            if (not mo_1.check_prop_match(**kwargs)):
                                exists = False
                        else:
                            exists = False

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
                        mo = IppoolPool(parent_mo_or_dn=module.params['org_dn'],
                                        name=ip['name'],
                                        descr=ip['descr'],
                                        assignment_order=ip['order'])

                        if 'last_addr' in ip and 'first_addr' in ip:
                            mo_1 = IppoolBlock(parent_mo_or_dn=mo,
                                               to=ip['last_addr'],
                                               r_from=ip['first_addr'],
                                               subnet=ip['subnet_mask'],
                                               def_gw=ip['default_gw'],
                                               prim_dns=ip['primary_dns'],
                                               sec_dns=ip['secondary_dns'])

                        if 'ipv6_last_addr' in ip and 'ipv6_first_addr' in ip:
                            mo_1 = IppoolIpV6Block(parent_mo_or_dn=mo,
                                                   to=ip['ipv6_last_addr'],
                                                   r_from=ip['ipv6_first_addr'],
                                                   prefix=ip['ipv6_prefix'],
                                                   def_gw=ip['ipv6_default_gw'],
                                                   prim_dns=ip['ipv6_primary_dns'],
                                                   sec_dns=ip['ipv6_secondary_dns'])
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
