#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}



DOCUMENTATION = '''
---
module: cisco_ucs_boot_policy
short_description: configures boot policy on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures boot policy on a cisco ucs server
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
        description: boot policy name
        required: true
    org_dn:
        description: org dn
        required: false
        default: "org-root"
    reboot_on_update:
        version_added: "1.0(1e)"
        description: reboots server if change in boot configuration
        required: false
        choices: ['yes', 'no']
        default: "no"
    enforce_vnic_name:
        version_added: "1.0(2d)"
        description: if not set, UCSM uses the vNIC or vHBA from the service profile
        required: false
        choices: ['yes', 'no']
        default: "yes"
    boot_mode:
        version_added: "2.2(1b)"
        description: boot mode
        required: false
        choices: ['legacy', 'uefi']
        default: "legacy"
    policy_owner:
        version_added: "2.1(1a)"
        description: policy owner
        required: false
        choices: ['local', 'pending-policy', 'policy']
        default: "local"
    descr:
        version_added: "1.0(1e)"
        description: description
        required: false

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_boot_policy:
    name: "test_boot_policy"
    org_dn: "org-root"
    reboot_on_update: "no"
    enforce_vnic_name: "no"
    boot_mode: "legacy"
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
                org_dn=dict(type='str', default="org-root"),
                reboot_on_update=dict(type='str', choices=['yes', 'no'], default="no"),
                enforce_vnic_name=dict(type='str', choices=['yes', 'no'], default="yes"),
                boot_mode=dict(type='str', choices=['legacy', 'uefi'], default="legacy"),
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


def setup_boot_policy(server, module):
    from ucsm_apis.server.boot import boot_policy_create
    from ucsm_apis.server.boot import boot_policy_exists
    from ucsm_apis.server.boot import boot_policy_delete

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = boot_policy_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        boot_policy_create(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        boot_policy_delete(server, mo.name, args_mo['org_dn'])

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_boot_policy(server, module)
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

