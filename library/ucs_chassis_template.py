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
module: ucs_chassis_profile_template
short_description: Configures Chassis Profile Templates on Cisco UCS Manager
description:
- Configures Chassis Profile Templates on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify Chassis Profile Templates are present and will create if needed.
    - If C(absent), will verify Chassis Profile Templates are absent and will delete if needed.
    choices: [present, absent]
    default: present
  name:
    description:
    - The name of the chassis profile template.
    - This name can be between 2 and 32 alphanumeric characters.
    - "You cannot use spaces or any special characters other than - (hyphen), \"_\" (underscore), : (colon), and . (period)."
    - This name must be unique across all chassis profiles and chassis profile templates within the same organization.
    required: yes
  template_type:
    description:
    - "The template type field which can be one of the following:"
    - "initial-template — Any chassis profiles created from this template are not updated if the template changes."
    - "updating-template — Any chassis profiles created from this template are updated if the template changes."
    choices: [initial-template, updating-template]
    default: initial-template
  description:
    description:
    - A user-defined description of the chassis profile template.
    - Enter up to 256 characters.
    - "You can use any characters or spaces except the following:"
    - "` (accent mark), \ (backslash), ^ (carat), \" (double quote), = (equal sign), > (greater than), < (less than), or ' (single quote)."
    aliases: [ descr ]
  maintenance_policy:
    description:
    - The name of the chassis maintenance policy you want to associate with chassis profiles created from this template.
	default: no maintenance policy
  firmware_package:
    description:
    - The name of the firmware package version you want to use with chassis profiles created from this template.
    default: no firmware package
  compute_connection_policy:
    description:
    - The name of the compute connection policy you want to associate with chassis profiles created from this template.
    default: no compute connection policy
  sas_expander_policy:
    description:
    - The name of the sas expander configuration policy you want to associate with chassis profiles created from this template.
	default: no sas expander configuration policy
  disk_zoning_policy: no disk zoning policy
    description:
    - The name of the disk zoning policy you want to associate with chassis profiles created from this template.
	default: no disk zoning policy
requirements:
- ucsmsdk
author:
- Olli Walsdorf (@owalsdor)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
- name: Configure Chassis Profile Template
  ucs_chassis_profile_template:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: S3260_Template
    template_type: updating-template
	maintenance_policy: S3260_Maint
	firmware_package: S3260_FW
	compute_connection_policy: S3260_Conn
	sas_expander_policy: S3260_SAS
	disk_zoning_policy: S3260_Disk

- name: Remove Service Profile Template
  ucs_service_profile_template:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: S3260_Template
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
		description=dict(type='str', default=''),
		template_type=dict(type='str', default='initial-template', choices=['initial-template', 'updating-template']),
		maintenance_policy=dict(type='str', default=''),
		firmware_package=dict(type='str', default=''),
		compute_connection_policy=dict(type='str', default=''),
		#sas_expander_policy=dict(type='str', default=''),
		disk_zoning_policy=dict(type='str', default=''),
		state=dict(type='str', default='present', choices=['present', 'absent']),
	)

	module = AnsibleModule(
		argument_spec,
		supports_check_mode=True,
	)
	ucs = UCSModule(module)

	err = False

	# UCSModule creation above verifies ucsmsdk is present and exits on failure.  Additional imports are done below.
	from ucsmsdk.mometa.equipment.EquipmentChassisProfile import EquipmentChassisProfile

	changed = False
	try:
		mo_exists = False
		props_match = False
		dn_base = 'org-root'
		dn = dn_base + '/cp-' + module.params['name']

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
				kwargs['descr'] = module.params['description']
				kwargs['chassis_fw_policy_name'] = module.params['firmware_package']
				kwargs['compute_conn_policy_name'] = module.params['compute_connection_policy']
				kwargs['disk_zoning_policy_name'] = module.params['disk_zoning_policy']
				if (mo.check_prop_match(**kwargs)):
					props_match = True
				
			if not props_match:
				if not module.check_mode:
					# create if mo does not already exist
					mo = EquipmentChassisProfile(
					parent_mo_or_dn=dn_base,
					name=module.params['name'],
					descr=module.params['description'],
					type=module.params['template_type'],
					maint_policy_name=module.params['maintenance_policy'],
					chassis_fw_policy_name=module.params['firmware_package'],
					compute_conn_policy_name=module.params['compute_connection_policy'],
					#sas_expander_config_policy_name=module.params['sas_expander_policy'],
					disk_zoning_policy_name=module.params['disk_zoning_policy']
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