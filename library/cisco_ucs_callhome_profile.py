#!/usr/bin/env python

from ansible.module_utils.basic import *


DOCUMENTATION = '''
---
module: cisco_ucs_callhome_profile
short_description: configures callhome profile on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures callhome profile on a cisco ucs server
Input Params:
    name:
        description: callhome profile name
        required: True
    format:
        description: message format
        required: False
        choices: ['fullTxt', 'shortTxt', 'xml']
        default: "xml"
    max_size:
        description: message max size
        required: False
    level:
        description: debug level
        required: False
        choices: ['critical', 'debug', 'disaster', 'fatal', 'major', 'minor',
        'normal', 'notification', 'warning']
        default: "debug"
    alert_groups:
        description: alert groups
        required: False
        choices: ['ciscoTac', 'diagnostic', 'environmental']
    descr:
        description: description
        required: False

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Rahul Gupta(ragupta4@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_callhome_profile:
    name: "testprofile"
    format: "xml"
    max_size: "10000"
    level: "debug"
    alert_groups: "ciscoTac"
    descr: "description"
    state: "present"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                name=dict(required=True, type='str'),
                format=dict(type='str',
                            choices=['fullTxt', 'shortTxt', 'xml'],
                            default="xml"),
                max_size=dict(type='str'),
                level=dict(type='str',
                    choices=['critical', 'debug', 'disaster', 'fatal',
                             'major', 'minor', 'normal', 'notification',
                             'warning'],
                    default="debug"),
                alert_groups=dict(type='str'),
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


def setup_callhome_profile(server, module):
    from ucsm_apis.admin.callhome import callhome_profile_create
    from ucsm_apis.admin.callhome import callhome_profile_delete
    from ucsm_apis.admin.callhome import callhome_profile_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = callhome_profile_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        callhome_profile_create(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        callhome_profile_delete(server, mo.name)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_callhome_profile(server, module)
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

