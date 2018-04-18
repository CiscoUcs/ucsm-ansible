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
module: ucs_chassis_sas
short_description: Creates Chassis SAS Expander Policy on Cisco UCS Manager
description:
- Configures Chassis SAS Expander Policy on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify Chassis SAS Expander Policy is present and will create if needed.
    - If C(absent), will verify Chassis SAS Expander Policy is absent and will delete if needed.
    choices: [present, absent]
    default: present
  name:
    description:
    - The name assigned to the Chassis SAS Expander Policy.
    - The Chassis SAS Expander Policy name is case sensitive.
    - This name can be between 1 and 16 alphanumeric characters.
    - "You cannot use spaces or any special characters other than - (hyphen), \"_\" (underscore), : (colon), and . (period)."
    - You cannot change this name after the Chassis SAS Expander Policy is created.
    required: yes
  description:
    description:
    - A description of the Chassis SAS Expander Package Policy.
    - Cisco recommends including information about where and when to use the policy.
    - Enter up to 256 characters.
    - "You can use any characters or spaces except the following:"
    - "` (accent mark), \ (backslash), ^ (carat), \" (double quote), = (equal sign), > (greater than), < (less than), or ' (single quote)."
    aliases: [ descr ]
  sas_policy:
	description:
	- Disabled: Connection Management is disabled in this policy and the Sas Expander uses only 6G speeds even if 12G is available.
	- Enabled: Connection Management is enabled in this policy and it intelligently shifts between 6G and 12 G speeds based on availability. Once 6G-12G Mixed Mode is enabled, you cannot downgrade to any release earlier than 3.2(3a). To downgrade, disable this mode.
    - No Change (Default): Pre-existing configuration is retained.
	- Note: Enabling or disabling 6G-12G Mixed Mode causes system reboot.
requirements:
- ucsmsdk
author:
- Olli Walsdorf (@owalsdor)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
- name: Add Chassis SAS Expander Policy
  ucs_chassis_maintenance:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: s3260_maint
	sas_policy: enabled
- name: Remove Chassis SAS Expander Policy
  ucs_chassis_maintenance:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: s3260_maint
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
		name=dict(type='str', required=True),
		description=dict(type='str', default=''),
		sas_policy=dict(type='str', default='default', choices=['disabled', 'enabled', 'default']),
		state=dict(type='str', default='present', choices=['present', 'absent']),
	)

	module = AnsibleModule(
		argument_spec,
		supports_check_mode=True,
		)
		
	ucs = UCSModule(module)

	err = False

	# UCSModule creation above verifies ucsmsdk is present and exits on failure, so additional imports are done below.
	from ucsmsdk.mometa.lstorage.LstorageSasExpanderConfigPolicy import LstorageSasExpanderConfigPolicy

	changed = False
	try:
		mo_exists = False
		props_match = False
		# dn is org-root/chassis-profile-maint-<name> for chassis maintenance policy
		dn_base = 'org-root'
		dn = dn_base + '/sas-expander-config-policy-' + module.params['name']

		mo = ucs.login_handle.query_dn(dn)
		if mo:
			mo_exists = True

		if module.params['state'] == 'absent':
			# mo must exist but all properties do not have to match
			if mo_exists:
				if not module.check_mode:
					ucs.login_handle.remove_mo(mo)
					ucs.login_handle.commit()
				changed = True
		else:
			if mo_exists:
				# check top-level mo props
				kwargs = dict(name=module.params['name'])
				kwargs['connection_Management'] = module.params['sas_policy']
				if (mo.check_prop_match(**kwargs)):
					props_match = True

			if not props_match:
				if not module.check_mode:
					# create if mo does not already exist
					mo = LstorageSasExpanderConfigPolicy(
					parent_mo_or_dn=dn_base,
					name=module.params['name'],
					descr=module.params['description'],
					connection_Management=module.params['sas_policy'],
					)

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
