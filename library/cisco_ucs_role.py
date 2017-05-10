#!/usr/bin/env python

from ansible.module_utils.basic import *


DOCUMENTATION = '''
---
module: cisco_ucs_role
short_description: configures role on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures role on a cisco ucs server
Input Params:
    name:
        description: role name
        required: True
    priv:
        description: role privilege (comma separated string)
        required: False
        choices: ['aaa', 'admin', 'ext-lan-config', 'ext-lan-policy',
        'ext-lan-qos', 'ext-lan-security', 'ext-san-config', 'ext-san-policy',
        'ext-san-qos', 'ext-san-security', 'fault', 'ls-compute', 'ls-config',
        'ls-config-policy', 'ls-ext-access', 'ls-network', 'ls-network-policy',
        'ls-qos', 'ls-qos-policy', 'ls-security', 'ls-security-policy',
        'ls-server', 'ls-server-oper', 'ls-server-policy', 'ls-storage',
        'ls-storage-policy', 'operations', 'org-management', 'pn-equipment',
        'pn-maintenance', 'pn-policy', 'pn-security', 'pod-config',
        'pod-policy', 'pod-qos', 'pod-security', 'power-mgmt', 'read-only']
        default: "read-only"
    policy_owner:
        description: policy owner
        required: False
        choices: ['local', 'pending-policy', 'policy']
        default: "local"
    descr:
        description: role description
        required: False

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Rahul Gupta(ragupta4@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_role:
    name: "testrole"
    priv: "read-only, fault"
    policy_owner: "local"
    descr: "description"
    state: "present"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                name=dict(required=True, type='str'),
                priv=dict(type='str'),
                policy_owner=dict(type='str',
                                choices=['local', 'pending-policy', 'policy'],
                                default="local"),
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


def setup_role(server, module):
    from ucsm_apis.admin.role import role_create
    from ucsm_apis.admin.role import role_delete
    from ucsm_apis.admin.role import role_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = role_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        role_create(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        role_delete(server, mo.name)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_role(server, module)
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

