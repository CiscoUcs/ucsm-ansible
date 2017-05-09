#!/usr/bin/env python

from ansible.module_utils.basic import *


DOCUMENTATION = '''
---
module: cisco_ucs_password_profile
short_description: configures profile strength of an user on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures profile strength of an user on a cisco ucs server
Input Params:
    min_passphrase_len:
        description: min passphrase length
        required: False
        default: "8"
    policy_owner:
        description: policy owner
        required: False
        choices: ['local', 'pending-policy', 'policy']
        default: "local"
    change_during_interval:
        description: Restricts the number of password changes, a locally
        authenticated user can make within a given number of hours.
        required: False
        choices: ['disable', 'enable']
        default: "disable"
    change_interval:
        description: change interval in hours, "1-745".Specifies the maximum
        number of hours over which the number of password changes specified
        in the change_count field are enforced.
        required: False
    no_change_interval:
        description: no change interval in hours, "1-745".Specifies the
        minimum number of hours that a locally authenticated user must wait
        before changing a newly created password.
        required: False
    history_count:
        description: history password count, "0-15".Specifies the number of
        unique passwords that a locally authenticated user must create before
        that user can reuse a previously used password.
        required: False
    change_count:
        description: change count, "0-10".Specifies the maximum number of
        times a locally authenticated user can change his or her password
        during the change_interval.
        required: False
    expiration_warn_time:
        description: expiration warning time
        required: False
    descr:
        description: description
        required: False

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Rahul Gupta(ragupta4@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_password_profile:
    min_passphrase_len:
    policy_owner:
    change_during_interval:
    change_interval:
    no_change_interval:
    history_count:
    change_count:
    expiration_warn_time:
    descr:
    state: "present"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                min_passphrase_len=dict(type='str', default="8"),
                policy_owner=dict(type='str', choices=['local', 'pending-policy', 'policy'], default="local"),
                change_during_interval=dict(type='str', choices=['disable', 'enable'], default="disable"),
                change_interval=dict(type='str'),
                no_change_interval=dict(type='str'),
                history_count=dict(type='str'),
                change_count=dict(type='str'),
                expiration_warn_time=dict(type='str'),
                descr=dict(type='str'),
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


def setup_password_profile(server, module):
    from ucsm_apis.admin.user import password_profile_modify
    from ucsm_apis.admin.user import password_profile_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = password_profile_exists(handle=server, **args_mo)

    if module.check_mode or exists:
        return not exists
    password_profile_modify(handle=server, **args_mo)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_password_profile(server, module)
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

