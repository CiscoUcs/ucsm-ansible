#!/usr/bin/env python

from ansible.module_utils.basic import *


DOCUMENTATION = '''
---
module: cisco_ucs_native_auth_console
short_description: configures native auth console on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures native auth console on a cisco ucs server
Input Params:
    realm:
        description: realm
        required: False
        choices: ['ldap', 'local', 'none', 'radius', 'tacacs']
    provider_group:
        description: provider group name
        required: False
    use2_factor:
        description: two factor authentication
        required: False
        choices: ['yes', 'no']
        default: "no"
    name:
        description: name
        required: False
    descr:
        description: description
        required: False

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Rahul Gupta(ragupta4@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_native_auth_console:
    realm: "radius"
    provider_group: "radius_provider_group"
    use2_factor: "yes"
    name: None
    descr: "description"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                realm=dict(type='str',
                        choices=['ldap', 'local', 'none', 'radius', 'tacacs']),
                provider_group=dict(type='str'),
                use2_factor=dict(type='str',
                                 choices=['yes', 'no'], default="no"),
                name=dict(type='str'),
                descr=dict(type='str'),
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
    argument_spec.update(_argument_mo())
    argument_spec.update(_argument_connection())

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


def setup_native_auth_console(server, module):
    from ucsm_apis.admin.auth import native_auth_console_configure
    from ucsm_apis.admin.auth import native_auth_console_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = native_auth_console_exists(handle=server, **args_mo)

    if module.check_mode or exists:
        return not exists
    native_auth_console_configure(handle=server, **args_mo)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_native_auth_console(server, module)
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

