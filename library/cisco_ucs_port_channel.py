#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}



DOCUMENTATION = '''
---
module: cisco_ucs_pc
short_description: configures port channels on cisco ucs manager
version_added: 0.9.0.0
description:
   -  configures port channels on cisco ucs manager
options:
    state:
        description:
         - if C(present), will perform create/add/enable operation
         - if C(absent), will perform delete/remove/disable operation
        required: false
        choices: ['present', 'absent']
        default: 'present'
    pc_list:
        description: list of pc dictionaries
        required: true

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_pc:
    pc_list:
      - {"name":"DDC-DTR-1"...
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                pc_list=dict(required=True, type='list'),
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


def setup_pc(server, module):
    from ucsmsdk.mometa.fabric.FabricEthLanPc import FabricEthLanPc
    from ucsmsdk.mometa.fabric.FabricEthLanPcEp import FabricEthLanPcEp
   
    ansible = module.params
    args_mo  =  _get_mo_params(ansible)

    changed = False

    for pc in args_mo['pc_list']:
        dn = 'fabric/lan/'+pc['fabric_id']
        mo = server.query_dn(dn+'/pc-'+pc['port_id'])
        if mo:
            exists = True
        else:
            exists = False

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
                    mo =  FabricEthLanPc(parent_mo_or_dn=dn,
	                                 name=pc['name'],
					 port_id=pc['port_id']

                                         )
                    for port in pc['port_list']:
		        mo_1 = FabricEthLanPcEp(parent_mo_or_dn=mo,
			                        eth_link_profile_name='default',
						name='',
						auto_negotiate='yes',
						slot_id=port['slot'],
						admin_state='enabled',
						port_id=port['port']
						)
                    server.add_mo(mo, True)
                    server.commit()

    return changed


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_pc(server, module)
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

