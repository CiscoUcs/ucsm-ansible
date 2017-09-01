#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}



DOCUMENTATION = '''
---
module: cisco_ucs_disk_group_policy
short_description: configures disk group policies on cisco ucs manager
version_added: 0.9.0.0
description:
   -  configures disk group policies on cisco ucs manager
options:
    state:
        description:
         - if C(present), will perform create/add/enable operation
         - if C(absent), will perform delete/remove/disable operation
        required: false
        choices: ['present', 'absent']
        default: 'present'
    disk_group_policy:
        description: disk group policy dictionary
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
  cisco_ucs_disk_group_policy:
    disk_group_policy:
      - {"name":"Docker-DG"...
    ucs_ip: "192.168.1.1"
    ucs_username: "admin"
    ucs_password: "password"
'''


def _argument_mo():
    return dict(
                disk_group_policy=dict(required=True, type='dict'),
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


def setup_disk_group_policy(server, module):
    from ucsmsdk.mometa.lstorage.LstorageDiskGroupConfigPolicy import LstorageDiskGroupConfigPolicy
    from ucsmsdk.mometa.lstorage.LstorageVirtualDriveDef import LstorageVirtualDriveDef
    from ucsmsdk.mometa.lstorage.LstorageLocalDiskConfigRef import LstorageLocalDiskConfigRef
   
    ansible = module.params
    args_mo  =  _get_mo_params(ansible)

    changed = False

    mo = server.query_dn(args_mo['org_dn']+'/disk-group-config-'+args_mo['disk_group_policy']['name'])
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
                mo = LstorageDiskGroupConfigPolicy(parent_mo_or_dn=args_mo['org_dn'],
                                                   raid_level=args_mo['disk_group_policy']['RAID_level'],
				                   name=args_mo['disk_group_policy']['name'])
                mo_1 = LstorageVirtualDriveDef(parent_mo_or_dn=mo,
                                               read_policy='platform-default',
				               drive_cache='platform-default',
                                               strip_size='platform-default',
				               io_policy='platform-default',
				               write_cache_policy='platform-default',
                                               access_policy='platform-default')
                if(len(args_mo['disk_group_policy']['disk_slot_numbers']) > 0):
                    for slot_num in args_mo['disk_group_policy']['disk_slot_numbers']:
                        mo_2 = LstorageLocalDiskConfigRef(parent_mo_or_dn=mo,
	                                                  slot_num=slot_num)
                server.add_mo(mo, True)
                server.commit()
    
    return changed


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_disk_group_policy(server, module)
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

