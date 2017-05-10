#!/usr/bin/env python

from ansible.module_utils.basic import *


DOCUMENTATION = '''
---
module: cisco_ucs_ldap_provider
short_description: configures ldap_provider on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures ldap_provider on a cisco ucs server
Input Params:
    name:
        description: ip address or hostname
        required: True
    order:
        description: lowest-available or 0-16
        required: False
        default: "lowest-available"
    rootdn:
        description: rootdn
        required: False
    basedn:
        description: basedn
        required: False
    port:
        description: port
        required: False
        default: "389"
    enable_ssl:
        description: enable ssl
        required: False
        choices: ['yes', 'no']
        default: "no"
    filter:
        description: filter
        required: False
    attribute:
        description: attribute
        required: False
    key:
        description: key
        required: False
    timeout:
        description: timeout
        required: False
        default: "30"
    vendor:
        description: vendor
        required: False
        choices: ['MS-AD', 'OpenLdap']
        default: "OpenLdap"
    retries:
        description: retries
        required: False
        default: "1"
    descr:
        description: ntp server description
        required: False

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Rahul Gupta(ragupta4@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_ldap_provider:
    name: "10.10.10.10"
    order: "2"
    rootdn: None
    basedn: ""
    port: "389"
    enable_ssl: "no"
    filter: None
    attribute: None
    key: None
    timeout: "30"
    vendor: "OpenLdap"
    retries: "1"
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
                rootdn=dict(type='str'),
                basedn=dict(type='str', default=""),
                port=dict(type='str', default="389"),
                enable_ssl=dict(type='str',
                                choices=['yes', 'no'], default="no"),
                filter=dict(type='str'),
                attribute=dict(type='str'),
                key=dict(type='str'),
                timeout=dict(type='str', default="30"),
                vendor=dict(type='str',
                            choices=['MS-AD', 'OpenLdap'], default="OpenLdap"),
                retries=dict(type='str', default="1"),
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


def setup_ldap_provider(server, module):
    from ucsm_apis.admin.ldap import ldap_provider_create
    from ucsm_apis.admin.ldap import ldap_provider_delete
    from ucsm_apis.admin.ldap import ldap_provider_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = ldap_provider_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        ldap_provider_create(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        ldap_provider_delete(server, mo.name)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_ldap_provider(server, module)
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

