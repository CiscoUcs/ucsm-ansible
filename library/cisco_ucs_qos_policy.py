#!/usr/bin/env python

from ansible.module_utils.basic import *

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}



DOCUMENTATION = '''
---
module: cisco_ucs_qos_policy
short_description: configures qos policy on a cisco ucs server
version_added: 0.9.0.0
description:
   -  configures qos policy on a cisco ucs server
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
        description: qos policy name
        required: true
    priority: 
        version_added: "1.0(1e)"
        description: fc, platinum, gold, silver, bronze, best-effort
        required: false
    burst:
        version_added: "1.0(1e)"
        description:  default 10240
        required: false
        
        
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
        description: list of qos mounts

requirements: ['ucsmsdk', 'ucsm_apis']
author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name:
  cisco_ucs_qos_policy:
    name: KUBAM
    descr: OS Boot VMedia
    retry: yes
    mounts:
    - name: VMware Install Media
      device: cdd
      protocol: http
      remote_ip: 172.28.225.135
      path: kubam
      file: service-profile-template
'''


def _argument_mo():
    return dict(
                name=dict(required=True, type='str'),
                priority=dict(required=True, type='str', 
                    choices=["platinum", "gold", 
                             "silver", "bronze", "best-effort"]),
                rate=dict(required=False, type='str', default="line-rate"),
                host_control=dict(required=False, type='str', 
                    choices=["full", "none"], default="none"),
                burst=dict(required=False, type='str', default="10240"),
                org_dn=dict(type='str', default="org-root"),
                descr=dict(type='str', default="")
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


def setup_qos_policy(server, module):
    from ucsmsdk.mometa.epqos.EpqosDefinition import EpqosDefinition
    from ucsmsdk.mometa.epqos.EpqosEgress import EpqosEgress

    print module
    ansible = module.params
    args_mo  =  _get_mo_params(ansible)
     
    changed = False
    policy = args_mo['name']    
    mo = server.query_dn(args_mo['org_dn']+"/ep-qos-"+policy)
    exists = False
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
                nmo = EpqosDefinition(
                    parent_mo_or_dn=args_mo['org_dn'],
                    name=args_mo['name'],
                    descr=args_mo['descr'])
                mo_x = EpqosEgress(parent_mo_or_dn=nmo,
                    rate=args_mo['rate'],   
                    host_control=args_mo['host_control'],
                    prio=args_mo['priority'],
                    burst=args_mo['burst'])

                server.add_mo(nmo, True) 
                server.commit()

    return changed

def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_qos_policy(server, module)
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

