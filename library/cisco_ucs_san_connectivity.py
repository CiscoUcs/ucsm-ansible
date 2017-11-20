#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}



DOCUMENTATION = '''
---
module: cisco_ucs_san_connectivity
short_description: configures san connectivity policies on cisco ucs manager
version_added: 0.9.0.0
description:
   -  configures san connectivity policies on cisco ucs manager
options:
    state:
        description:
         - if C(present), will perform create/add/enable operation
         - if C(absent), will perform delete/remove/disable operation
        required: false
        choices: ['present', 'absent']
        default: 'present'
    san_conn_list:
        description: list of san conn dictionaries
        required: true
    org_dn:
        description: org dn
        required: false
        default: "org-root"

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_san_connectivity:
    san_conn_list:
      - {"name":"Docker-DTR"...
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                san_conn_list=dict(required=True, type='list'),
                org_dn=dict(type='str', default="org-root"),
    )

def _argument_custom():
    return dict(
        state=dict(default='present',
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


def setup_san_connectivity(server, module):
    from ucsmsdk.mometa.vnic.VnicSanConnPolicy import VnicSanConnPolicy
    from ucsmsdk.mometa.vnic.VnicFcNode import VnicFcNode
    from ucsmsdk.mometa.vnic.VnicFc import VnicFc
    from ucsmsdk.mometa.vnic.VnicFcIf import VnicFcIf

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)

    changed = False

    for san_conn in args_mo['san_conn_list']:
        exists = False
        mo = server.query_dn(args_mo['org_dn']+'/san-conn-pol-'+san_conn['name'])
        if mo:
            exists = True

        if ansible['state'] == 'absent':
            if exists:
                changed = True
                if not module.check_mode:
                    server.remove_mo(mo)
                    server.commit()
        else:
            if not exists:
                changed = True
                if not module.check_mode:
                    # create if mo does not already exist
	            mo = VnicSanConnPolicy(parent_mo_or_dn=args_mo['org_dn'],
	                                   name=san_conn['name'])
	            mo_1 = VnicFcNode(parent_mo_or_dn=mo,
	                              ident_pool_name=san_conn['wwnn_pool'],
			              addr='pool-derived')
                    for vhba in san_conn['vhba_list']:
                        mo_2 = VnicFc(parent_mo_or_dn=mo,
		                      adaptor_profile_name=vhba['adapter_policy'],
			              order=vhba['order'],
			              name=vhba['name'],
			              nw_templ_name=vhba['vhba_template'])
	                mo_2_1 = VnicFcIf(parent_mo_or_dn=mo_2, name='default')
                    server.add_mo(mo, True)
                    server.commit()
    
    return changed


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_san_connectivity(server, module)
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

