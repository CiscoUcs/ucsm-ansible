#!/usr/bin/python

# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.


from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}



DOCUMENTATION = '''
---
module: cisco_ucs_boot_order
short_description: Configures boot order on a cisco ucs server.
version_added: "0.9.0.0"
description:
   -  Configures boot order on a cisco ucs server.
options:
    name:
        version_added: "1.0(1e)"
        description: boot policy name
        required: true
    devices:
        description: list of dictionary
    {"device_name": "", "device_order": "", "property_name": "property_value"}
        required: true
    org_dn:
        description: org dn
        required: false
        default: "org-root"

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_boot_order:
    name: "test_boot_policy"
    devices:
      - {"device_name": "sdcard", "device_order": "1"}
      - {"device_name": "iscsi", "device_order": "2", "vnic_name": "vnic_pri"}
      - {"device_name": "efi", "device_order": "3"}
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                name=dict(required=True, type='str'),
                devices=dict(required=True, type='list'),
                org_dn=dict(type='str', default="org-root"),
    )


def _argument_connection():
    return  dict(
        # UcsHandle
        ucs_server=dict(type='dict'),

        # Ucs server credentials
        ucs_ip=dict(type='str'),
        ucs_username=dict(default="admin", type='str'),
        ucs_password=dict(type='str', no_log=True),
        ucs_port=dict(default=None),
        ucs_secure=dict(default=None),
        ucs_proxy=dict(default=None)
    )



def _ansible_module_create():
    argument_spec = dict()
    argument_spec.update(_argument_connection())
    argument_spec.update(_argument_mo())

    return AnsibleModule(argument_spec,
                         supports_check_mode=True)



def _get_mo_params(params):
    from ansible.module_utils.cisco_ucs import UcsConnection
    args = {}
    for key in _argument_mo():
        if params.get(key) is None:
            continue
        args[key] = params.get(key)
    return args


def setup_boot_order(server, module):
    from ucsm_apis.server.boot import boot_policy_order_set
    from ucsm_apis.server.boot import boot_policy_order_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = boot_policy_order_exists(handle=server, **args_mo)

    if module.check_mode or exists:
        return not exists
    boot_policy_order_set(handle=server, **args_mo)
    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_boot_order(server, module)
    except Exception as e:
        err = True
        result["msg"] = "setup error: %s " % str(e)
        result["changed"] = False

    return result, err


def main():
    from ansible.module_utils.cisco_ucs import UcsConnection

    module = _ansible_module_create()
    conn = UcsConnection(module)
    server = conn.login()
    result, err = setup(server, module)
    conn.logout()
    if err:
        module.fail_json(**result)
    module.exit_json(**result)


if __name__ == '__main__':
    main()

