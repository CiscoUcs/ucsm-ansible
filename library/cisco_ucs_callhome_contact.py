#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cisco_ucs_callhome_contact
short_description: configures callhome contact on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures callhome contact on a cisco ucs server
options:
    contact:
        version_added: "1.0(1e)"
        description: contact name
        required: true
    phone:
        version_added: "1.0(1e)"
        description: phone number e.g. +91-1234567890
        required: true
    email:
        version_added: "1.0(1e)"
        description: contact email address
        required: true
    addr:
        version_added: "1.0(1e)"
        description: contact address
        required: true
    customer:
        version_added: "1.0(1e)"
        description: customer id
        required: true
    contract:
        version_added: "1.0(1e)"
        description: contract id
        required: true
    site:
        version_added: "1.0(1e)"
        description: site id
        required: true
    r_from:
        version_added: "1.0(1e)"
        description: from email address
        required: true
    reply_to:
        version_added: "1.0(1e)"
        description: to email address
        required: true
    urgency:
        version_added: "1.0(1e)"
        description: alert priority
        required: false
        choices: ['alert', 'critical', 'debug', 'emergency', 'error', 'info',
         'notice', 'warning']
        default: "debug"

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_callhome_contact:
    contact: "username"
    phone: "+91-1234567890"
    email: "user@cisco.com"
    addr: "user address"
    customer: "1111"
    contract: "2222"
    site: "3333"
    r_from: "from@cisco.com"
    reply_to: "to@cisco.com"
    urgency: "debug"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                contact=dict(required=True, type='str'),
                phone=dict(required=True, type='str'),
                email=dict(required=True, type='str'),
                addr=dict(required=True, type='str'),
                customer=dict(required=True, type='str'),
                contract=dict(required=True, type='str'),
                site=dict(required=True, type='str'),
                r_from=dict(required=True, type='str'),
                reply_to=dict(required=True, type='str'),
                urgency=dict(type='str',
                        choices=['alert', 'critical', 'debug', 'emergency',
                                 'error', 'info', 'notice', 'warning'],
                        default="debug"),
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


def setup_callhome_contact(server, module):
    from ucsm_apis.admin.callhome import callhome_contact_update
    from ucsm_apis.admin.callhome import callhome_contact_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = callhome_contact_exists(handle=server, **args_mo)

    if module.check_mode or exists:
        return not exists
    callhome_contact_update(handle=server, **args_mo)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_callhome_contact(server, module)
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

