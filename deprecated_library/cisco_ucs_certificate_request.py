#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cisco_ucs_certificate_request
short_description: configures certifcate request for a keyring  on a cisco ucs
server
version_added: 0.9.0.0
description:
   -  configures certifcate request for a keyring on a cisco ucs server
options:
    state:
        description:
         - if C(present), will perform create/add/enable operation
         - if C(absent), will perform delete/remove/disable operation
        required: false
        choices: ['present', 'absent']
        default: "present"
    name:
        description: key ring name
        required: true
    ip:
        version_added: "1.0(1e)"
        description: ipv4 ip address
        required: false
        default: "0.0.0.0"
    ip_a:
        version_added: "2.1(2a)"
        description: ipv4 ip address for fi 'a'
        required: false
        default: "0.0.0.0"
    ip_b:
        version_added: "2.1(2a)"
        description: ipv4 ip address for fi 'b'
        required: false
        default: "0.0.0.0"
    ipv6:
        version_added: "2.2(1b)"
        description: ipv6 ip address
        required: false
        default: "::"
    ipv6_a:
        version_added: "2.2(1b)"
        description: ipv6 ip address for fi 'a'
        required: false
        default: "::"
    ipv6_b:
        version_added: "2.2(1b)"
        description: ipv6 ip address for fi 'b'
        required: false
        default: "::"
    dns:
        version_added: "2.0(2m)"
        description: dns server ip address
        required: false
    locality:
        version_added: "2.0(2m)"
        description: locality
        required: false
    state_name:
        description: state
        required: false
    country:
        version_added: "2.0(2m)"
        description: country
        required: false
    org_name:
        version_added: "2.0(2m)"
        description: organization name
        required: false
    org_unit_name:
        version_added: "2.0(2m)"
        description: organization unit name
        required: false
    subj_name:
        version_added: "1.0(1e)"
        description: subject
        required: false
    email:
        version_added: "2.0(2m)"
        description: email
        required: false
    pwd:
        version_added: "1.0(1e)"
        description: password
        required: false

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_certificate_request:
    name: "testkeyring"
    ip: "0.0.0.0"
    ip_a: "0.0.0.0"
    ip_b: "0.0.0.0"
    ipv6: "::"
    ipv6_a: "::"
    ipv6_b: "::"
    dns: "10.10.10.10"
    locality: "locality"
    state_name: "state"
    country: "country"
    org_name: "organization_name"
    org_unit_name: "organization_unit_name"
    subj_name: "subject"
    email: "email_address"
    pwd: "password"
    state: "present"
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                name=dict(required=True, type='str'),
                ip=dict(type='str', default="0.0.0.0"),
                ip_a=dict(type='str', default="0.0.0.0"),
                ip_b=dict(type='str', default="0.0.0.0"),
                ipv6=dict(type='str', default="::"),
                ipv6_a=dict(type='str', default="::"),
                ipv6_b=dict(type='str', default="::"),
                dns=dict(type='str'),
                locality=dict(type='str'),
                state_name=dict(type='str'),
                country=dict(type='str'),
                org_name=dict(type='str'),
                org_unit_name=dict(type='str'),
                subj_name=dict(type='str'),
                email=dict(type='str'),
                pwd=dict(type='str'),
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
        if key == 'state_name':
            args['state'] = params.get(key)
            continue
        args[key] = params.get(key)
    return args


def setup_certificate_request(server, module):
    from ucsm_apis.admin.keyring import certificate_request_create
    from ucsm_apis.admin.keyring import certificate_request_delete
    from ucsm_apis.admin.keyring import certificate_request_exists

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
    exists, mo = certificate_request_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        certificate_request_create(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        certificate_request_delete(server, args_mo['name'])

    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_certificate_request(server, module)
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

