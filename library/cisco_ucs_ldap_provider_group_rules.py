#!/usr/bin/env python

from ansible.module_utils.basic import *


DOCUMENTATION = '''
---
module: cisco_ucs_ldap_provider_group_rules
short_description: configures group rules of ldap provider on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures group rules of ldap provider on a cisco ucs server
Input Params:
    ldap_provider_name:
        description: ldap provider name
        required: True
    authorization:
        description: group authorization
        required: False
        choices: ['disable', 'enable']
        default: "enable"
    traversal:
        description: group recursion
        required: False
        choices: ['non-recursive', 'recursive']
        default: "recursive"
    target_attr:
        description: target atribute
        required: False
        default: "memberOf"
    use_primary_group:
        description: use primary group
        required: False
        choices: ['yes', 'no']
        default: "no"
    name:
        description: name
        required: False
    descr:
        description: description
        required: False

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Rahul Gupta(ragupta4@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_ldap_provider_group_rules:
    ldap_provider_name: "test_ldap_provider"
    authorization: "enable"
    traversal:"recursive"
    target_attr: "memberOf"
    use_primary_group: "no"
    name: None
    descr: "description"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                ldap_provider_name=dict(required=True, type='str'),
                authorization=dict(type='str',
                                   choices=['disable', 'enable'],
                                   default="enable"),
                traversal=dict(type='str',
                               choices=['non-recursive', 'recursive'],
                               default="recursive"),
                target_attr=dict(type='str', default="memberOf"),
                use_primary_group=dict(type='str',
                                       choices=['yes', 'no'], default="no"),
                name=dict(type='str'),
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


def setup_ldap_provider_group_rules(server, module):
    from ucsm_apis.admin.ldap import ldap_provider_group_rules_configure
    from ucsm_apis.admin.ldap import ldap_provider_group_rules_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = ldap_provider_group_rules_exists(handle=server, **args_mo)

    if module.check_mode or exists:
        return not exists
    ldap_provider_group_rules_configure(handle=server, **args_mo)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_ldap_provider_group_rules(server, module)
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

