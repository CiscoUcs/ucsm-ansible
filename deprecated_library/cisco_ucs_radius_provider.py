#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cisco_ucs_radius_provider
short_description: configures radius_provider on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures radius_provider on a cisco ucs server
options:
    state:
        description:
         - if C(present), will perform create/add/enable operation
         - if C(absent), will perform delete/remove/disable operation
        required: false
        choices: ['present', 'absent']
        default: "present"
    name:
        version_added: "1.0(1e)"
        description: ip address or hostname
        required: true
    order:
        version_added: "1.1(1j)"
        description: lowest-available or 0-16
        required: false
        default: "lowest-available"
    key:
        version_added: "1.0(1e)"
        description: key
        required: false
    auth_port:
        version_added: "1.0(1e)"
        description: authorization port
        required: false
        default: "1812"
    timeout:
        version_added: "1.4(1i)"
        description: timeout
        required: false
        default: "5"
    retries:
        version_added: "1.4(1i)"
        description: retries
        required: false
        default: "1"
    enc_key:
        version_added: "1.0(1e)"
        description: encryption key
        required: false
    descr:
        version_added: "1.0(1e)"
        description: description
        required: false

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_radius_provider:
    name: "test_radius_provider"
    order: "lowest-available"
    key: "testkey"
    auth_port: "1812"
    timeout: "5"
    retries: "1"
    enc_key: "encryption_key"
    descr: "description"
    state: "present"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                name=dict(required=True, type='str'),
                order=dict(type='str', default="lowest-available"),
                key=dict(type='str'),
                auth_port=dict(type='str', default="1812"),
                timeout=dict(type='str', default="5"),
                retries=dict(type='str', default="1"),
                enc_key=dict(type='str'),
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


def setup_radius_provider(server, module):
    from ucsm_apis.admin.radius import radius_provider_create
    from ucsm_apis.admin.radius import radius_provider_delete
    from ucsm_apis.admin.radius import radius_provider_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = radius_provider_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        radius_provider_create(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        radius_provider_delete(server, mo.name)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_radius_provider(server, module)
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

