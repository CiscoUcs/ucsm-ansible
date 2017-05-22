#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cisco_ucs_keyring
short_description: configures keyring on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures keyring on a cisco ucs server
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
        description: key ring name
        required: true
    modulus:
        version_added: "1.0(1e)"
        description: modulus
        required: false
        choices: ['mod2048', 'mod2560', 'mod3072', 'mod3584', 'mod4096', 'modinvalid']
        default: "mod2048"
    regen:
        version_added: "1.0(1e)"
        description: regen
        required: false
        choices: ['yes', 'no']
        default: "no"
    policy_owner:
        version_added: "2.1(1a)"
        description: policy owner
        required: false
        choices: ['local', 'pending-policy', 'policy']
        default: "local"
    tp:
        version_added: "1.0(1e)"
        description: trusted point name
        required: false
    cert:
        version_added: "1.0(1e)"
        description: certificate text
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
  cisco_ucs_keyring:
    name: "testkeyring"
    modulus: "mod2048"
    regen: "no"
    policy_owner: "local"
    tp: "testtp"
    cert: "certificatetext"
    descr: "description"
    state: "present"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                name=dict(required=True, type='str'),
                modulus=dict(type='str',
                        choices=['mod2048', 'mod2560', 'mod3072', 'mod3584',
                                 'mod4096', 'modinvalid'],
                        default="mod2048"),
                regen=dict(type='str', choices=['yes', 'no'], default="no"),
                policy_owner=dict(type='str',
                        choices=['local', 'pending-policy', 'policy'],
                        default="local"),
                tp=dict(type='str'),
                cert=dict(type='str'),
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


def setup_keyring(server, module):
    from ucsm_apis.admin.keyring import key_ring_create
    from ucsm_apis.admin.keyring import key_ring_delete
    from ucsm_apis.admin.keyring import key_ring_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = key_ring_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        key_ring_create(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        key_ring_delete(server, mo.name)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_keyring(server, module)
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

