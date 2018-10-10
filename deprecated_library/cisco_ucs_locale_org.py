#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cisco_ucs_locale_org
short_description: configures org for the locale on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures organization for the locale on a cisco ucs server
options:
    state:
        description:
         - if C(present), will perform create/add/enable operation
         - if C(absent), will perform delete/remove/disable operation
        required: false
        choices: ['present', 'absent']
        default: "present"
    locale_name:
        description: locale name
        required: true
    name:
        version_added: "1.0(1e)"
        description: org name
        required: true
    org_dn:
        description: org dn
        required: false
        default: "org-root"
    descr:
        version_added: "1.0(1e)"
        description: assigned org description
        required: false

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_locale_org:
    locale_name: "testlocale"
    name: "test_locale_org"
    org_dn: "org-root"
    descr: "description"
    state: "present"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                locale_name=dict(required=True, type='str'),
                name=dict(required=True, type='str'),
                org_dn=dict(type='str', default="org-root"),
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


def setup_locale_org(server, module):
    from ucsm_apis.admin.locale import locale_org_assign
    from ucsm_apis.admin.locale import locale_org_unassign
    from ucsm_apis.admin.locale import locale_org_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = locale_org_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        locale_org_assign(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        locale_org_unassign(server, args_mo['locale_name'], mo.name)

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_locale_org(server, module)
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

