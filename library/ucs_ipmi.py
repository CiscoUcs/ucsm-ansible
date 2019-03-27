#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: ucs_ipmi

short_description: Configures IPMI Policy Cisco UCS Manager

description:
  - Configures IPMI Policy on Cisco UCS Manager.
  - Examples can be used with the UCS Platform Emulator U(https://cs.co/ucspe).

extends_documentation_fragment: ucs

options:
  state:
    description:
      - If C(present), will verify IPMI policy is present and will create or update if needed.
      - If C(absent), will verify IPMI policy is absent and will delete if needed.
    choices: [present, absent]
    default: present

  name:
    description:
      - The name of the IPMI policy.
      - This name can be between 1 and 16 alphanumeric characters.
      - 'You cannot use spaces or any special characters other than - (hyphen), _ (underscore), : (colon), and . (period).'
      - You cannot change this name after the IPMI policy is created.
    required: yes

  descrption:
    description:
      - A description of the IPMI Policy.
      - Enter up to 256 characters.
      - "Any characters or spaces can be used except the following:"
      - "` (accent mark), \ (backslash), ^ (carat), \" (double quote), = (equal sign), > (greater than), < (less than), or ' (single quote)."
    aliases: [ descr ]

  ipmi_over_lan:
    description:
      - Enable or Disable IPMI over LAN.
      - "This can be one of the following:"
      - "enable - IPMI is enabled, Service Profiles using this policy will allow IPMI."
      - "disable - IPMI is disabled, Service Profiles using this policy will not allow IPMI."
    choices: [enable, disable]
    required: yes

  org_dn:
    description:
      - The distinguished name (dn) of the organization where the resource is assigned.
    default: org-root

requirements:
  - ucsmsdk

author:
  - John McDonough (@johnamcdonough)
  - CiscoUcs (@CiscoUcs)

version_added: '2.8'
'''

EXAMPLES = r'''
- name: Configure IPMI Policy
  ucs_ipmi:
    hostname: 10.10.10.20
    username: admin
    password: password
    name: ipmi-pol
    description: Policy to enable IPMI
    ipmi_over_lan: enable
    org_dn: org-root/org-PROD
    delegate_to: localhost
    state: present

- name: Remove IPMI Policy
  ucs_ipmi:
    hostname: 10.10.10.20
    username: admin
    password: password
    name: ipmi-pol
    ipmi_over_lan: enable
    org_dn: org-root/org-PROD
    delegate_to: localhost
    state: absent
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec


def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(
        org_dn=dict(type='str', default='org-root'),
        name=dict(type='str', required=True),
        description=dict(type='str', aliases=['descr']),
        ipmi_over_lan=dict(type='str', required=True, choices=['enable', 'disable']),
        delegate_to=dict(type='str', default='localhost'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'present', ['name']],
        ],
    )
    # UCSModule verifies ucsmsdk is present and exits on failure.  Imports are below ucs object creation.
    # Imports are below for UCS object creation.
    ucs = UCSModule(module)

    from ucsmsdk.mometa.aaa.AaaEpAuthProfile import AaaEpAuthProfile

    err = False
    changed = False
    requested_state = module.params['state']

    kwargs = dict(
        ipmi_over_lan=module.params['ipmi_over_lan']
    )

    if module.params['description'] is not None:
        kwargs['descr'] = module.params['description']

    try:
        dn = module.params['org_dn'] + '/auth-profile-' + module.params['name']
        mo = ucs.login_handle.query_dn(dn)

        # Determine state change
        if mo:
            # Object exists, if it should exist has anything changed?
            if requested_state == 'present':
                # Do some or all Object properties not match, that is a change
                if not mo.check_prop_match(**kwargs):
                    changed = True

        # Object does not exist but should, that is a change
        else:
            if requested_state == 'present':
                changed = True

        # Object exists but should not, that is a change
        if mo and requested_state == 'absent':
            changed = True

        # Apply state if not check_mode
        if changed and not module.check_mode:
            if requested_state == 'absent':
                ucs.login_handle.remove_mo(mo)
            else:
                kwargs['parent_mo_or_dn'] = module.params['org_dn']
                kwargs['name'] = module.params['name']
                kwargs['ipmi_over_lan'] = module.params['ipmi_over_lan']
                if module.params['description'] is not None:
                    kwargs['descr'] = module.params['description']

                mo = AaaEpAuthProfile(**kwargs)
                ucs.login_handle.add_mo(mo, modify_present=True)

            try:
                ucs.login_handle.commit()
            except Exception as e:
                err = True
                ucs.result['msg'] = "Module error: %s " % str(e)

    except Exception as e:
        err = True
        ucs.result['msg'] = "Module error: %s " % str(e)

    ucs.result['changed'] = changed
    if err:
        module.fail_json(**ucs.result)

    module.exit_json(**ucs.result)


if __name__ == '__main__':
    main()
