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
module: ucs_storage_local_disk_s_series.py
short_description: Sets the drive to either unconfigured good or jbod in UCS Manager for S-Series servers.
description:
- Sets the disk state from jobd to unconfigured good or vice versa in Cisco UCS Manager.
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:

  chassis_id:
    description:
    - Specify the chassis id number.
    - For setting the disk state in multiple chassis at a time, provide first chassis id and total number of chassis as
      comma separated values.
    - For example, chassis_id: 1, 10 - in this example 1 represents the first chassis.
    - and 10 represents the total number of chassis on which the operation has to be performed.

  blade_id:
    description:
    - Specify the server id number.
    - For multiple server options, provide first server id and total number of servers as
      comma separated values.
    - For example, blade_id: 1, 2 - in this example 1 represents the first server.
    - and 2 represents the total number of servers on which the operation has to be performed.
	
  blade_enc:
    description:
    - This parameter takes true or false as the value.
    - When set to true, it expects the enc_id to be either 3 or 4 or both.
    - When set to false, it defaults the enc_id to 1.
    - enc_id: 1 represents the chassis storage enclosure and this can take the value from 1 to 56 as it supports 56 disks.
    - enc_id: 3 or 4 represents the server storage enclosures. enc_id: 3 is for boot disks and enc_id: 4 supports NVMe disks.
  
  enc_id:
    description:
    - Specify the storage enc id number.
    - This field is required when the blade_enc is true.
    - For setting multiple enclosure ids, provide first enclosure id and total number of enclosures as
      comma separated values.
    - For example, enc_id: 3 - in this example 3 represents the first storage enclosure in the blade server.
    - Note: enc_id is always 1 for chassis storage enclosure, hence there is no need to specifically set this value.
    - However, for server specific storage enclosures the enc_id can either be 3 or 4.

  disk_id:
    description:
    - Specify the disk id number.
    - For setting multiple disk ids, provide first disk id and total number of disks as
      comma separated values.
    - For example, disk_id: 1, 2 - in this example 1 represents the first disk.
    - and 2 represents the total number of disks on which the operation has to be performed.
    
  disk_state:
    description:
    - Specify the disk state. The allowed options are unconfigured-good and jbod.

requirements:
- ucsmsdk
author:
- sindhu sudhir (@sisudhir)
- CiscoUcs (@CiscoUcs)

version_added: '2.5'
'''

EXAMPLES = r'''

- The following examples is for changing disk state for the disks in the server storage enclosure.
- The first example shows how to change the disk state for a single blade, chassis and enclosure.
- The second example shows how to change the disk state for multiple blades, chassis and enclosures. 
 
ucs_storage_local_disk_s_series:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    chassis_id: 1
    blade_id: 1
    blade_enc: true
    enc_id: 3
    disk_id: 201, 2
    disk_state: "jbod"
	
ucs_storage_local_disk_s_series:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    chassis_id: 1, 3
    blade_id: 1, 2
    blade_enc: true
    enc_id: 3, 2
    disk_id: 201, 2
    disk_state: "unconfigured-good"	

    ---

- The following examples is for changing disk state for the disks in the chassis storage enclosure.
- The first example shows how to change the disk state for a single blade, chassis.
- The second example shows how to change the disk state for multiple blades, chassis.

ucs_storage_local_disk_s_series:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    chassis_id: 1
    blade_enc: false
    disk_id: 1, 56
    disk_state: "jbod"
	
ucs_storage_local_disk_s_series:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    chassis_id: 1, 3
    blade_enc: false
    disk_id: 1, 56
    disk_state: "unconfigured-good"

    ---

    It's a best practice to use the -i option of ansible-playbook
    to specify an inventory file when configuring multiple hosts.

    When using an inventory file, the variables defined in the
    inventory file are used

ucs_storage_local_disk_s_series:
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    chassis_id: 1, 3
    blade_id: 1, 2
    blade_enc: true
    enc_id: 3, 2
    disk_id: 201, 2
    disk_state: "unconfigured-good"	
	
    ---
	
ucs_storage_local_disk_s_series:
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    chassis_id: 1, 3
    blade_id: 1, 2
    blade_enc: false
    disk_id: 1, 56
    disk_state: "unconfigured-good"

    ---	

- Using the check mode and retry options you can wait till the desired state is reached
- For this, you need to run the task twice with the same parameters specified as shown in the example below
- While the first one does the commit or updates the dn, the second one checks if the desired state is reached
- You can increase the retries number based on number of chassis/ blades 

ucs_storage_local_disk_s_series:
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    chassis_id: 1
    disk_id: 1, 56
    blade_enc: False
    disk_state: "jbod"
 
ucs_storage_local_disk_s_series:
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    chassis_id: 1
    disk_id: 1, 56
    blade_enc: False
    disk_state: "jbod"
check_mode: yes
register: result
until: result.changed == False
retries: 120
delay: 10


'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec

def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(chassis_id=dict(type='str', required=True),
                         blade_id=dict(type='str', choices=['1', '2', '1, 2']),
                         enc_id=dict(type='str', choices=['3', '4', '3, 2']),
                         disk_id=dict(type='str', required=True), 
                         blade_enc=dict(type='str', required=True, choices=['True', 'False']),
                         disk_state=dict(type='str', required=True, choices=['jbod', 'unconfigured-good']))

    module = AnsibleModule(argument_spec,
                           supports_check_mode=True,
                           required_if=[
                           ['blade_enc', 'True', ['blade_id']], 
                           ['blade_enc', 'True', ['enc_id']], ] ) 

    ucs = UCSModule(module)

    from ucsmsdk.mometa.storage.StorageLocalDisk import StorageLocalDisk 
    err = False
    changed = False

    try:
        dn_base = 'sys'

        num_chassis = 1
        chassis_list = module.params['chassis_id'].split(',')
        chassis_id_start = int( chassis_list[0] )
        if( len(chassis_list) > 1 ):
            num_chassis = int( chassis_list[1] )
       
        if( module.params['blade_enc'] == 'True' ): 
            num_blades = 1
            blade_list = module.params['blade_id'].split(',')
            blade_id_start = int( blade_list[0] )
            if( len(blade_list) > 1 ):
                num_blades = int( blade_list[1] )

            num_encs = 1
            enc_list = module.params['enc_id'].split(',')
            enc_id_start = int( enc_list[0] )
            if( len(enc_list) > 1 ):
                num_encs = int( enc_list[1] )

        num_disks = 1
        disk_list = module.params['disk_id'].split(',')
        disk_id_start = int( disk_list[0] )
        if( len(disk_list) > 1 ):
            num_disks = int( disk_list[1] )

        if( module.params['blade_enc'] == 'True' ): 
            for chassis_num in range( chassis_id_start, chassis_id_start + num_chassis ):
                dn_chassis_base = dn_base + '/chassis-' + str( chassis_num )

                for blade_num in range( blade_id_start, blade_id_start + num_blades ):
                    dn_blade_base = dn_chassis_base + '/blade-' + str( blade_num )

                    for enc_num in range( enc_id_start, enc_id_start + num_encs ):
                        dn_enc_base = dn_blade_base  + '/enc-' + str( enc_num )

                        for disk_num in range( disk_id_start, disk_id_start + num_disks ):
                            dn = dn_enc_base + '/disk-' + str( disk_num ) 

                            existing_mo = ucs.login_handle.query_dn(dn)
                            if existing_mo:
                                kwargs = dict(disk_state = module.params['disk_state'])
                                if not existing_mo.check_prop_match(**kwargs):
                                    if not module.check_mode:
                                        existing_mo.admin_action_trigger = "triggered"
                                        existing_mo.admin_action = module.params['disk_state']
                                        ucs.login_handle.add_mo(existing_mo, True)
                                        ucs.login_handle.commit()
                                    changed = True
        else:
            for chassis_num in range( chassis_id_start, chassis_id_start + num_chassis ):
                dn_chassis_base = dn_base + '/chassis-' + str( chassis_num )

                for disk_num in range( disk_id_start, disk_id_start + num_disks ):
                    dn = dn_chassis_base + '/enc-1/disk-' + str( disk_num )

                    existing_mo = ucs.login_handle.query_dn(dn)
                    if existing_mo:
                        kwargs = dict(disk_state = module.params['disk_state'])
                        if not existing_mo.check_prop_match(**kwargs):
                            if not module.check_mode:
                                existing_mo.admin_action_trigger = "triggered"
                                existing_mo.admin_action = module.params['disk_state']
                                ucs.login_handle.add_mo(existing_mo, True)
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
