#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}



DOCUMENTATION = '''
---
module: cisco_ucs_spt
short_description: configures service profile templates on cisco ucs manager
version_added: 0.9.0.0
description:
   -  configures service profile templates on cisco ucs manager
options:
    state:
        description:
         - if C(present), will perform create/add/enable operation
         - if C(absent), will perform delete/remove/disable operation
        required: false
        choices: ['present', 'absent']
        default: 'present'
    spt_list:
        description: list of spt dictionaries
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
  cisco_ucs_spt:
    spt_list:
      - {"name":"Docker-DTR"...
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                spt_list=dict(required=True, type='list'),
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


def setup_spt(server, module):
    from ucsmsdk.mometa.ls.LsServer import LsServer
    from ucsmsdk.mometa.ls.LsRequirement import LsRequirement
    from ucsmsdk.mometa.lstorage.LstorageProfileBinding import LstorageProfileBinding
    from ucsmsdk.mometa.vnic.VnicEther import VnicEther
    from ucsmsdk.mometa.vnic.VnicConnDef import VnicConnDef
   
    ansible = module.params
    args_mo  =  _get_mo_params(ansible)

    changed = False

    for spt in args_mo['spt_list']:
        mo = server.query_dn(args_mo['org_dn']+'/ls-'+spt['name'])
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
                    if not 'vmedia_policy' in spt:
                        spt['vmedia_policy'] = ''
                    mo =  LsServer(parent_mo_or_dn=args_mo['org_dn'],
	                           name=spt['name'],
                                   type=spt['template_type'],
                                   resolve_remote='yes',
                                   descr='',
                                   usr_lbl='',
                                   src_templ_name='',
                                   ext_ip_state='pooled',
                                   ext_ip_pool_name='ext-mgmt',
                                   ident_pool_name=spt['uuid_pool'],
                                   vcon_profile_name='',
                                   agent_policy_name='',
                                   bios_profile_name=spt['bios_policy'],
                                   boot_policy_name=spt['boot_policy'],
                                   dynamic_con_policy_name='',
                                   host_fw_policy_name=spt['host_fw_package'],
                                   kvm_mgmt_policy_name='',
                                   local_disk_policy_name='',
                                   maint_policy_name='',
                                   mgmt_access_policy_name='',
                                   mgmt_fw_policy_name='',
                                   power_policy_name='',
                                   scrub_policy_name='',
                                   sol_policy_name='',
                                   stats_policy_name='',
                                   vmedia_policy_name=spt['vmedia_policy']
                                   )
                    if 'server_pool' in spt: 
                        mo_1 = LsRequirement(parent_mo_or_dn=mo, name=spt['server_pool'])
                    if 'storage_profile' in spt:
                        mo_1 = LstorageProfileBinding(parent_mo_or_dn=mo, storage_profile_name=spt['storage_profile'])
                    if 'san_connectivity_policy' in spt:
                        mo_1 = VnicConnDef(parent_mo_or_dn=mo,
		                           san_conn_policy_name=spt['san_connectivity_policy'])
                    if 'vnic_list' in spt: 
                        for vnic in spt['vnic_list']:
                            if(vnic['vnic_name'] <> '' and vnic['vnic_template'] <> ''):
                                mo_1 = VnicEther(parent_mo_or_dn=mo, adaptor_profile_name=vnic['vnic_adapter_policy'], order=vnic['vnic_order'], name=vnic['vnic_name'], nw_templ_name=vnic['vnic_template'])

                    if(spt['lan_connectivity_policy'] <> ''):
                        mo_x = VnicConnDef(parent_mo_or_dn=mo,
                                    lan_conn_policy_name=spt['lan_connectivity_policy'])
    # create server pool and add to template.
                    server.add_mo(mo, True)
                    server.commit()
    
    return changed


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_spt(server, module)
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

