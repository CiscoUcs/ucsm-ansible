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
module: ucs_chassis_zoning
short_description: Configures Chassis Disk Zoning on Cisco UCS Manager
description:
- Configures Chassis Disk ZOning on Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify Chassis Disk Zoning is present and will create if needed.
    - If C(absent), will verify Chassis Disk ZOning is absent and will delete if needed.
    choices: [present, absent]
    default: present
  name:
    description:
    - The name of the Disk Zoning Policy.
    - This name can be between 1 and 32 alphanumeric characters.
    - You cannot use spaces or any special characters other than - (hyphen), \"_\" (underscore), : (colon), and . (period).
    - You cannot change this name after the Disk Zoning Policy is created.
    required: yes
  descrption:
    description:
    - A description of the Disk Zoning Policy.
    - Enter up to 256 characters.
    - "You can use any characters or spaces except the following:"
    - "` (accent mark), \ (backslash), ^ (carat), \" (double quote), = (equal sign), > (greater than), < (less than), or ' (single quote)."
    aliases: [ descr ]
  preserve_config:
    description:
    - If this check box is selected, it preserves all configuration related information for the disks such as slot number, ownership, server assigned, controller assigned, and controller type..
    choices: [checked, unchecked]
    default: unchecked
  ownership:
	description:
	- The slot ownership value. This can be one of the following:
	choices: [unassigned, dedicated, shared, chassis-global-spare]
	required: yes
	default: unassigned
	
	Choice dedicated:
	server_id:
	- The ID of the server that the disk is assigned.
	choices: [1, 2]
	default: ''
	controller_id:
	- The ID of the controller that the disk is assigned.
	choices: [1, 2]
	default: ''
	controller type:
	- The type for the controller. If the disk is either dedicated or shared, the controller type is always SAS.
	default: SAS
	
	Choice Shared or Chassis Global Hot Spare
	default: ''
  drive_path: -> future implementation
	description:
	- The disk path the disk is connected to.
	choices: [PATH-BOTH, PATH-0, PATH-1]
	default: PATH-BOTH
  slot_range:
    description:
    - The slot number for the disk
	- Valid input (1-60, comma(,), hyphen(-) and no negative numbers)
    required: yes
	default: ''
requirements:
- ucsmsdk
author:
- Olli Walsdorf (@owalsdor)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
- name: Configure chassis disk zoning policy
  ucs_chassis_zoning:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: S3260_1
    ownership: dedicated
    server_id: 1
    controller_id: 1
	slot_range: 1-4,9-28
- name: Configure chassis disk zoning
  ucs_chassis_zoning:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: S3260_2
    ownership: shared
    drive_path: path_0
	slot_range: 1-28
- name: Remove chassis disk zoning policy
  ucs_chassis_zoning:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: S3260_1
    state: absent
'''

RETURN = r'''
#
'''

from itertools import chain
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec

def parse_range(rng):
    parts = rng.split('-')
    if 1 > len(parts) > 2:
        raise ValueError("Bad range: '%s'" % (rng,))
    parts = [int(i) for i in parts]
    start = parts[0]
    end = start if len(parts) == 1 else parts[1]
    if start > end:
        end, start = start, end
    return range(start, end + 1)
	
def parse_range_list(rngs):
    return sorted(set(chain(*[parse_range(rng) for rng in rngs.split(',')])))


def main():
	argument_spec = ucs_argument_spec
	argument_spec.update(
		org_dn=dict(type='str', default='org-root'),
		name=dict(type='str', required=True),
		descr=dict(type='str', default=''),
		preserve_config=dict(type='str', default='no', choices=['yes', 'no']),
		ownership=dict(type='str', default='unassigned', choices=['unassigned', 'dedicated', 'shared', 'chassis-global-spare']),
		#drive_path=dict(type='str', default='PATH-BOTH', choices=['PATH-BOTH', 'PATH-0', 'PATH-1']),
		server_id=dict(type='str', default='', choices=['1', '2']),
		controller_id=dict(type='str', default='', choices=['1', '2']),
		controller_type=dict(type='str', default='SAS'),
		slot_range=dict(type='str'),
		state=dict(default='present', choices=['present', 'absent'], type='str'),
	)
	module = AnsibleModule(
		argument_spec,
		supports_check_mode=True,
	)
	# UCSModule verifies ucsmsdk is present and exits on failure.  Imports are below ucs object creation.
	ucs = UCSModule(module)

	err = False

	from ucsmsdk.mometa.lstorage.LstorageControllerRef import LstorageControllerRef
	from ucsmsdk.mometa.lstorage.LstorageDiskSlot import LstorageDiskSlot
	from ucsmsdk.mometa.lstorage.LstorageDiskZoningPolicy import LstorageDiskZoningPolicy

	changed = False
	try:
		mo_exists = False
		props_match = False
		# dn is <org_dn>/disk-zoning-policy-<name>
		dn = module.params['org_dn'] + '/disk-zoning-policy-' + module.params['name']
		mo = ucs.login_handle.query_dn(dn)
		if mo:
			mo_exists = True

		if module.params['state'] == 'absent':
			if mo_exists:
				if not module.check_mode:
					ucs.login_handle.remove_mo(mo)
					ucs.login_handle.commit()
				changed = True
		else:
			if mo_exists:
				# check top-level mo props
				kwargs = dict(name=module.params['name'])
				kwargs['descr'] = module.params['descr']
				if (mo.check_prop_match(**kwargs)):
					if module.params['slot_range']:
						filter_zoning = '(name, ' + module.params['name'] + ' ,type="eq")'
						mo_1 = ucs.login_handle.query_classid("LstorageDiskZoningPolicy", filter_str=filter_zoning)
						for i in mo_1:
							mo_2 = ucs.login_handle.query_children(in_mo=i, class_id="LStorageDiskSlot")
							mo_3 = []
							for j in mo_2:
								mo_3.append(j.id)
							mo_4 = sorted(map(int,mo_3))
							mo_5 = list(parse_range_list(module.params['slot_range']))
							if mo_4 == mo_5:
								props_match = True
					else:
						props_match = True

			if not props_match:
				if not module.check_mode:
					# create if mo does not already exist
					mo = LstorageDiskZoningPolicy(
						parent_mo_or_dn=module.params['org_dn'],
						name=module.params['name'],
						descr=module.params['descr'],
						preserve_config=module.params['preserve_config'],
					)
					
					for i in list(parse_range_list(module.params['slot_range'])):
						mo_1 = LstorageDiskSlot(
							parent_mo_or_dn=mo,
							id=str(i),
							ownership=module.params['ownership'],
							#drive_path=module.params['drive_path'],
						)
						if module.params['ownership'] == 'dedicated':
							mo_2 = LstorageControllerRef(
								parent_mo_or_dn=mo_1,
								controller_id=module.params['controller_id'],
								server_id=module.params['server_id'],
								controller_type=module.params['controller_type'],
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