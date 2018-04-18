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
module: ucs_chassis_maintenance
short_description: Creates Chassis Maintenance Policy on Cisco UCS Manager
description:
- Configures Chassis Maintenance Policy on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify Chassis Maintenance Policy is present and will create if needed.
    - If C(absent), will verify Chassis Maintenance Policy is absent and will delete if needed.
    choices: [present, absent]
    default: present
  name:
    description:
    - The name assigned to the Chassis Maintenance Policy.
    - The Chassis Maintenance Policy name is case sensitive.
    - This name can be between 1 and 16 alphanumeric characters.
    - "You cannot use spaces or any special characters other than - (hyphen), \"_\" (underscore), : (colon), and . (period)."
    - You cannot change this name after the Chassis Maintenance Policy is created.
    required: yes
  description:
    description:
    - A description of the Chassis Maintenance Package Policy.
    - Cisco recommends including information about where and when to use the policy.
    - Enter up to 256 characters.
    - "You can use any characters or spaces except the following:"
    - "` (accent mark), \ (backslash), ^ (carat), \" (double quote), = (equal sign), > (greater than), < (less than), or ' (single quote)."
    aliases: [ descr ]
  reboot_policy:
	description:
	- When a chassis profile is associated with a chassis, or when changes are made to a chassis profile that is already associated with a chassis, you must reboot the chassis to complete the process. 
	- The Reboot Policy field determines when the reboot occurs for chassis associated with any chassis profiles that include this maintenance policy. 
	- This can only be the following:
	- User Ack—The user must reboot the chassis manually after the chassis profile association is complete or changes are made.
requirements:
- ucsmsdk
author:
- Olli Walsdorf (@owalsdor)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
- name: Add Chassis Maintenance Policy
  ucs_chassis_maintenance:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: s3260_maint
- name: Remove Chassis Maintenance Policy
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
		state=dict(type='str', default='present', choices=['present', 'absent']),
	)

	module = AnsibleModule(
		argument_spec,
		supports_check_mode=True,
		)
		
	ucs = UCSModule(module)

	err = False

	# UCSModule creation above verifies ucsmsdk is present and exits on failure, so additional imports are done below.
	from ucsmsdk.mometa.cpmaint.CpmaintMaintPolicy import CpmaintMaintPolicy

	changed = False
	try:
		mo_exists = False
		props_match = False
		# dn is org-root/chassis-profile-maint-<name> for chassis maintenance policy
		dn_base = 'org-root'
		dn = dn_base + '/chassis-profile-maint-' + module.params['name']

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
				if (mo.check_prop_match(**kwargs)):
					props_match = True

			if not props_match:
				if not module.check_mode:
					# create if mo does not already exist
					mo = CpmaintMaintPolicy(
					parent_mo_or_dn=dn_base,
					name=module.params['name'],
					descr=module.params['description'],
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
