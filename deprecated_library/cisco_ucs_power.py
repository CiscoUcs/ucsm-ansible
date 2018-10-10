#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}



DOCUMENTATION = '''
---
module: cisco_ucs_power
short_description: configures server power on a  cisco ucs server
version_added: 0.9.0.0
description:
   -  configures server power on a cisco ucs server
options:
    state:
        description:
         - if C(on), will power on the server
         - if C(off), will power off the server
         - if C(cycle-wait), will trigger a graceful OS shutdown and
         powercycle operation on the specified server.
         - if Ccycle-immediate), will trigger an immediate powercycle
         operation on the specified server.
        required: true
        choices: ['on', 'off', "cycle-wait", "cycle-immediate"]
        default:
    chassis_id:
        description: chassis id
        required: false
    blade_id:
        description: blade id
        required: false
    rack_id:
        description: rack id
        required: false

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_power:
    chassis_id: "1"
    blade_id: "1"
    state: "on"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
- name:
  cisco_ucs_power:
    rack_id: "1"
    state: "on"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                chassis_id=dict(required=False, type='str'),
                blade_id=dict(required=False, type='str'),
                rack_id=dict(required=False, type='str'),
    )


def _argument_custom():
    return dict(
        state=dict(choices=['on', 'off', "cycle-wait", "cycle-immediate"],
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
    argument_spec.update(_argument_connection())
    argument_spec.update(_argument_mo())
    argument_spec.update(_argument_custom())

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


def setup_power(server, module):
    from ucsm_apis.server.power import server_power_exists
    from ucsm_apis.server.power import server_power_on
    from ucsm_apis.server.power import server_power_off
    from ucsm_apis.server.power import server_power_cycle_wait
    from ucsm_apis.server.power import server_power_cycle_immediate

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists = server_power_exists(handle=server, **args_mo)

    if ansible["state"] == "on":
        if module.check_mode or exists:
            return not exists
        server_power_on(handle=server, **args_mo)
    elif ansible["state"] == "off":
        if module.check_mode or not exists:
            return exists
        server_power_off(handle=server, **args_mo)
    else:
        if module.check_mode:
            return True
        if ansible["state"] == "cycle-wait":
            server_power_cycle_wait(handle=server, **args_mo)
        elif ansible["state"] == "cycle-immediate":
            server_power_cycle_immediate(handle=server, **args_mo)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_power(server, module)
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

