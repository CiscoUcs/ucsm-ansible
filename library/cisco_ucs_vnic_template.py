#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}



DOCUMENTATION = '''
---
module: cisco_ucs_vnic_template
short_description: configures vnic template on cisco ucs manager
version_added: 0.9.0.0
description:
   -  configures vnic templates on cisco ucs manager
options:
    state:
        description:
         - if C(present), will perform create/add/enable operation
         - if C(absent), will perform delete/remove/disable operation
        required: false
        choices: ['present', 'absent']
        default: 'present'
    vnic_list:
        description: list of vnic dictionaries
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
  cisco_ucs_vnic_template:
    vnic_list:
      - {"name":"DDC-DTR-1"...
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                vnic_list=dict(required=True, type='list'),
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


def setup_vnic_template(server, module):
    from ucsmsdk.mometa.vnic.VnicLanConnTempl import VnicLanConnTempl
    from ucsmsdk.mometa.vnic.VnicEtherIf import VnicEtherIf
   
    ansible = module.params
    args_mo  =  _get_mo_params(ansible)

    changed = False

    for vnic in args_mo['vnic_list']:
        exists = False
        mo = server.query_dn(args_mo['org_dn']+'/lan-conn-templ-'+vnic['name'])
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
                    #if not "description" in vnic:
                    #    vnic["description"] = "" 
                    #if not "qos_policy_name" in vnic:
                    #    vnic["qos_policy_name"] = ""
                    if not "mtu" in vnic:
                        vnic["mtu"] = "1500"
	            mo = VnicLanConnTempl(parent_mo_or_dn=args_mo['org_dn'],
                                          descr=vnic['description'],    
	                                  ident_pool_name=vnic['mac_pool'],
				          name=vnic['name'],
                                          mtu=vnic['mtu'],
                                          #qos_policy_name=vnic['qos_policy_name'],
		    		          switch_id=vnic['side'])

                    # make the first network the native vlan
                    def_net = "yes" 
                    for v in vnic['vlan']:
	                mo_1 = VnicEtherIf(parent_mo_or_dn=mo, 
                                        default_net=def_net, 
                                        name=v)
                        if def_net == "yes":
                            def_net = "no"

                    server.add_mo(mo, True)
                    server.commit()

    return changed


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_vnic_template(server, module)
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

