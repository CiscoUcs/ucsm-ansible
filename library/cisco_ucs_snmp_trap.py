#!/usr/bin/env python

from ansible.module_utils.basic import *


DOCUMENTATION = '''
---
module: cisco_ucs_snmp_trap
short_description: configures snmp trap on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures snmp trap on a cisco ucs server
Input Params:
    hostname:
        description: hostname or ip address
        required: True
    community:
        description: community or username
        required: True
    port:
        description: port
        required: False
        default: "162"
    version:
        description: version
        required: False
        choices: ['v1', 'v2c', 'v3']
        default: "v2c"
    notification_type:
        description: notification type
        required: False
        choices: ['informs', 'traps']
        default: "traps"
    v3_privilege:
        description: privilege for version "v3", required only for version 'v3'
        required: False
        choices: ['noauth', 'priv']
        default: "noauth"

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Rahul Gupta(ragupta4@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_snmp_trap:
    hostname: '10.10.10.10'
    community: 'community'
    port: "162"
    version: "v3"
    notification_type: "traps"
    v3_privilege: "noauth"
    state: "present"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                hostname=dict(required=True, type='str'),
                community=dict(required=True, type='str'),
                port=dict(type='str', default="162"),
                version=dict(type='str',
                             choices=['v1', 'v2c', 'v3'], default="v2c"),
                notification_type=dict(type='str',
                            choices=['informs', 'traps'], default="traps"),
                v3_privilege=dict(type='str',
                            choices=['noauth', 'priv'], default="noauth"),
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


def setup_snmp_trap(server, module):
    from ucsm_apis.admin.snmp import snmp_trap_add
    from ucsm_apis.admin.snmp import snmp_trap_remove
    from ucsm_apis.admin.snmp import snmp_trap_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = snmp_trap_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        snmp_trap_add(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        snmp_trap_remove(server, mo.hostname)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_snmp_trap(server, module)
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

