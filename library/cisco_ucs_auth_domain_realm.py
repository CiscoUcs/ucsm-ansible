#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cisco_ucs_auth_domain_realm
short_description: configures auth domain realm on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures authentication domain realm on a cisco ucs server
options:
    domain_name:
        description: auth domain name
        required: true
    realm:
        version_added: "1.4(1i)"
        description: realm
        required: false
        choices: ['ldap', 'local', 'none', 'radius', 'tacacs']
        default: "local"
    use2_factor:
        version_added: "2.2(1b)"
        description: two factor authentication
        required: false
        choices: ['yes', 'no']
        default: "no"
    provider_group:
        version_added: "1.4(1i)"
        description: provider group name
        required: false
        default: ""
    name:
        version_added: "1.4(1i)"
        description: name
        required: false
    descr:
        version_added: "1.4(1i)"
        description: description
        required: false

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_auth_domain_realm:
    domain_name: "testdomain"
    realm: "radius"
    use2_factor: "yes"
    provider_group: "test_radius_provider_group"
    name: None
    descr: None
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                domain_name=dict(required=True, type='str'),
                realm=dict(type='str',
                           choices=['ldap', 'local', 'none', 'radius',
                                    'tacacs'],
                           default="local"),
                use2_factor=dict(type='str', choices=['yes', 'no'],
                                 default="no"),
                provider_group=dict(type='str', default=""),
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


def setup_auth_domain_realm(server, module):
    from ucsm_apis.admin.auth import auth_domain_realm_configure
    from ucsm_apis.admin.auth import auth_domain_realm_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = auth_domain_realm_exists(handle=server, **args_mo)

    if module.check_mode or exists:
        return not exists
    auth_domain_realm_configure(handle=server, **args_mo)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_auth_domain_realm(server, module)
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

