#!/usr/bin/env python

from ansible.module_utils.basic import *


DOCUMENTATION = '''
---
module: cisco_ucs_password_strength
short_description: configures password strength of an user on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures password strength of an user on a cisco ucs server
Input Params:
    policy_owner:
        description: policy owner
        required: False
        choices: ['local', 'pending-policy', 'policy']
        default: "local"
    descr:
        description: description
        required: False

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Rahul Gupta(ragupta4@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_password_strength:
    policy_owner:
    descr:
    state: "present"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                policy_owner=dict(type='str', choices=['local', 'pending-policy', 'policy'], default="local"),
                descr=dict(type='str'),
    )


def _argument_custom():
    return dict(
        state=dict(default="present",
                   choices=['present', 'absent'],
                   type='str'),
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
    argument_spec.update(_argument_custom())
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


def setup_password_strength(server, module):
    from ucsm_apis.admin.user import password_strength_check
    from ucsm_apis.admin.user import password_strength_uncheck
    from ucsm_apis.admin.user import password_strength_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = password_strength_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        password_strength_check(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        password_strength_uncheck(server)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_password_strength(server, module)
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

