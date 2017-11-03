#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}



DOCUMENTATION = '''
---
module: cisco_ucs_bios_policy
short_description: configures bios policy on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures bios policy on a cisco ucs server
options:
    state:
        description:
         - if C(present), will perform create/add/enable operation
         - if C(absent), will perform delete/remove/disable operation
        required: false
        choices: ['present', 'absent']
        default: "present"
    name:
        version_added: "1.0(1e)"
        description: bios policy name
        required: true
    org_dn:
        description: org dn
        required: false
        default: "org-root"
    descr:
        version_added: "1.0(1e)"
        description: description of the policy
        required: false
        default: empty
    retry:
        version_added: "1.0(1e)"
        description: should the policy keep trying to mount on failure
        required: false
        choices: ['yes', 'no']
        default: yes
    mounts:
        version_added: "1.0(1e)"
        description: list of bios mounts

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_bios_policy:
    name: KUBAM
    descr: Destroy disk when dissasociated. 
    ucs_ip: 192.168.1.1
    ucs_username: admin
    ucs_password: Cisco.123
'''


def _argument_mo():
    return dict(
                name=dict(required=True, type='str'),
                org_dn=dict(type='str', default="org-root"),
                descr=dict(required=False, type='str', default=""),
                reboot_on_update=dict(required=False, 
                                choices=['yes', 'no'],
                                type='str', default="no"),
                resume_on_power_loss=dict(required=False,
                                choices=['last-state', 'platform-default'],
                                type='str', default="platform-default"),
                cdn_control=dict(required=False, 
                                choices=['enabled', 'disabled'],
                                type='str', default="disabled")
    )


def _argument_custom():
    return dict(
        state=dict(default="present",
                   choices=['present', 'absent'],
                   type='str')
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


def setup_bios_policy(server, module):
    from ucsmsdk.mometa.bios.BiosVProfile import BiosVProfile
    from ucsmsdk.mometa.bios.BiosVfConsistentDeviceNameControl import BiosVfConsistentDeviceNameControl
    from ucsmsdk.mometa.bios.BiosVfFrontPanelLockout import BiosVfFrontPanelLockout
    from ucsmsdk.mometa.bios.BiosVfPOSTErrorPause import BiosVfPOSTErrorPause
    from ucsmsdk.mometa.bios.BiosVfQuietBoot import BiosVfQuietBoot
    from ucsmsdk.mometa.bios.BiosVfResumeOnACPowerLoss import BiosVfResumeOnACPowerLoss
    

    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
     
    changed = False
    exists = False
    policy = args_mo['name']    
    mo = server.query_dn(args_mo['org_dn']+"/bios-prof-"+policy)
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
                if not 'reboot_on_update' in args_mo: 
                    args_mo['reboot_on_update'] = "no"
                mo = BiosVProfile(
                    parent_mo_or_dn=args_mo['org_dn'],
                    name=args_mo['name'],
                    reboot_on_update=args_mo['reboot_on_update'],
                    descr=args_mo['descr'])
                
                if 'reboot_on_power_loss' in args_mo:
                    m_1 = BiosVfResumeOnACPowerLoss(parent_mo_or_dn=mo, vp_resume_on_ac_power_loss=args_mo['reboot_on_power_loss'])            
                # consistent device naming.  
                if 'cdn_control' in args_mo: 
                    mo_2 = BiosVfConsistentDeviceNameControl(parent_mo_or_dn=mo, vp_cdn_control="enabled")
                
                server.add_mo(mo, True) 
                server.commit()

    return changed

def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_bios_policy(server, module)
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

