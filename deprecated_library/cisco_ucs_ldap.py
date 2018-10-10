#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cisco_ucs_ldap
short_description: configures ldap on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures ldap on a cisco ucs server
options:
    timeout:
        version_added: "1.0(1e)"
        description: timeout
        required: false
        default: "30"
    attribute:
        version_added: "1.0(1e)"
        description: attribute
        required: false
        default: "CiscoAvPair"
    filter:
        version_added: "1.0(1e)"
        description: filter
        required: false
        default: "cn=$userid"
    retries:
        version_added: "1.0(1e)"
        description: retries
        required: false
        default: "1"
    policy_owner:
        version_added: "2.1(1a)"
        description: policy_owner
        required: false
        choices: ['local', 'pending-policy', 'policy']
        default: "local"
    basedn:
        version_added: "1.0(1e)"
        description: basedn
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
  cisco_ucs_ldap:
    timeout: "30"
    attribute: "CiscoAvPair"
    filter: "cn=$userid"
    retries: "1"
    policy_owner: "local"
    basedn: None
    descr: "description"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                timeout=dict(type='str', default="30"),
                attribute=dict(type='str', default="CiscoAvPair"),
                filter=dict(type='str', default="cn=$userid"),
                retries=dict(type='str', default="1"),
                policy_owner=dict(type='str',
                                choices=['local', 'pending-policy', 'policy'],
                                default="local"),
                basedn=dict(type='str'),
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


def setup_ldap(server, module):
    from ucsm_apis.admin.ldap import ldap_configure
    from ucsm_apis.admin.ldap import ldap_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = ldap_exists(handle=server, **args_mo)

    if module.check_mode or exists:
        return not exists
    ldap_configure(handle=server, **args_mo)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_ldap(server, module)
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

