#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cisco_ucs_role
short_description: configures role on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures role on a cisco ucs server
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
        description: role name
        required: true
    priv:
        version_added: "1.0(1e)"
        description: role privilege. single privilege or multiple comma
         separated privileges. valid values are
         C(aaa), C(admin), C(ext-lan-config), C(ext-lan-policy),
         C(ext-lan-qos), C(ext-lan-security), C(ext-san-config),
         C(ext-san-policy), C(ext-san-qos), C(ext-san-security), C(fault),
         C(ls-compute), C(ls-config), C(ls-config-policy), C(ls-ext-access),
         C(ls-network), C(ls-network-policy), C(ls-qos), C(ls-qos-policy),
         C(ls-security), C(ls-security-policy), C(ls-server),
         C(ls-server-oper), C(ls-server-policy), C(ls-storage),
         C(ls-storage-policy), C(operations), C(org-management),
         C(pn-equipment), C(pn-maintenance), C(pn-policy), C(pn-security),
         C(pod-config), C(pod-policy), C(pod-qos), C(pod-security),
         C(power-mgmt), C(read-only)
        required: false
        choices:
        default: "read-only"
    policy_owner:
        version_added: "2.1(1a)"
        description: policy owner
        required: false
        choices: ['local', 'pending-policy', 'policy']
        default: "local"
    descr:
        version_added: "1.0(1e)"
        description: role description
        required: false

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
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

