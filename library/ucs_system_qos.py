#!/usr/bin/env python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ucs_system_qos
short_description: Configures system QoS settings
version_added: 0.9.0.0
description:
   -  Configures system QoS settings
options:
    priority:
        description: Priority to configure
        choices: ["best-effort", "bronze", "fc", "gold","platinum", "silver"]
        required: true
    admin_state:
        description: Admin state of QoS Policy
        choices: ['disabled', 'enabled']
        required: false
    cos:
        description: CoS setting
        choices: ['any', '[0-6]']
        required: true
    weight:
        description: CoS profile weight
        choices: ['best-effort', "none", "0-10"]
        required: false
    mtu:
        description: MTU size
        choices: ['fc", "normal', '0-4294967295']
        required: false
    multicast_optimize:
        description: Set multicast optimization options
        choices: ['false', 'no', 'true', 'yes']
        required: false
    drop:
        description: Set multicast optimization options
        default='no-drop'
        choices: ['drop", "no-drop']
        required: false
requirements: ['ucsmsdk']
author: "Brett Johnson (@sdbrett)"
'''

EXAMPLES = '''
- name:
  ucs_system_qos:
    priority: platinum
    admin_state: enabled
    multicast_optimize: no
    weight: 5
    cos: 6
    mtu: 9216
    hostname: 192.168.99.100
    username: admin
    password: password
'''


# TODO Add ranges for cos, weight and mtu


def main():
    from ansible.module_utils.basic import AnsibleModule
    from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec

    argument_spec = ucs_argument_spec
    argument_spec.update(
        priority=dict(required=True, type='str', choices=["best-effort", "bronze", "fc", "gold", "platinum", "silver"]),
        cos=dict(required=False, type='str'),
        weight=dict(required=False, type='str', default=''),
        admin_state=dict(required=False, type='str', default='', choices=['disabled', 'enabled']),
        drop=dict(required=False, type='str', default='no-drop', choices=['drop', 'no-drop']),
        mtu=dict(required=False, type='str', default=''),
        multicast_optimize=dict(required=False, type='str', default='no', choices=['false', 'no', 'true', 'yes']),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )
    ucs = UCSModule(module)

    err = False

    changed = False
    try:
        props_match = False
        dn = "fabric/lan/classes/class-" + module.params['priority']
        mo = ucs.login_handle.query_dn(dn)
        # check top-level mo props
        if module.params['priority'] == 'best-effort':
            kwargs = dict(weight=module.params['weight'])
            kwargs['mtu'] = module.params['mtu']
            kwargs['multicast_optimize'] = module.params['multicast_optimize']
            if mo.check_prop_match(**kwargs):
                props_match = True
            else:
                if not module.check_mode:
                    mo.weight = module.params['weight']
                    mo.mtu = module.params['mtu']
                    mo.multicast_optimize = module.params['multicast_optimize']
                    ucs.login_handle.add_mo(mo, True)
                    ucs.login_handle.commit()
                changed = True
        elif module.params['priority'] == 'fc':
            kwargs = dict(weight=module.params['weight'])
            kwargs['cos'] = module.params['cos']
            if mo.check_prop_match(**kwargs):
                props_match = True
            else:
                if not module.check_mode:
                    mo.weight = module.params['weight']
                    mo.cos = module.params['cos']
                    ucs.login_handle.add_mo(mo, True)
                    ucs.login_handle.commit()
                changed = True

        else:
            kwargs = dict(weight=module.params['weight'])
            kwargs['priority'] = module.params['priority']
            kwargs['mtu'] = module.params['mtu']
            kwargs['cos'] = module.params['cos']
            kwargs['drop'] = module.params['drop']
            kwargs['admin_state'] = module.params['admin_state']
            kwargs['multicast_optimize'] = module.params['multicast_optimize']
        if mo.check_prop_match(**kwargs):
            props_match = True
        else:
            if not module.check_mode:
                mo.weight = module.params['weight']
                mo.mtu = module.params['mtu']
                mo.cos = module.params['cos']
                mo.drop = module.params['drop']
                mo.admin_state = module.params['admin_state']
                mo.multicast_optimize = module.params['multicast_optimize']

                ucs.login_handle.add_mo(mo, True)
                ucs.login_handle.commit()
            changed = True

    except Exception as e:
        err = True
        ucs.result['msg'] = "setup error: %s " % str(e)

    ucs.result['changed'] = changed
    if err:
        module.fail_json(**ucs.result)
    module.exit_json(**ucs.result)


if __name__ == '__main__':
    main()