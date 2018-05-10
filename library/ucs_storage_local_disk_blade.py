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
module: ucs_storage_local_disk_blade.py
short_description: Sets the drive to either unconfigured good or jbod in UCS Manager
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
    - For example, blade_id: 1, 8 - in this example 1 represents the first server.
    - and 8 represents the total number of servers on which the operation has to be performed.

  slot_id:
    description:
    - Specify the adapter slot id number. slot_id represents the SAS/SATA drives in the server.
    - For setting multiple slots ids, provide first slot id and total number of slots as
      comma separated values.
    - For example, slot_id: 1, 3 - in this example 1 represents the first slot.
    - and 3 represents the total number of slots on which the operation has to be performed.

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
ucs_storage_local_disk_blade:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    chassis_id: 2
    blade_id: 2, 6
    slot_id: 1
    disk_id: 1, 2
    disk_state: "jbod"

    ---

ucs_storage_local_disk_blade:
    hostname: 10.0.1.10
    username: my_username
    password: my_password
    chassis_id: 2
    blade_id: 2, 6
    slot_id: 1
    disk_id: 1, 2
    disk_state: "unconfigured-good"

    ---

    It's a best practice to use the -i option of ansible-playbook
    to specify an inventory file when configuring multiple hosts.

    When using an inventory file, the variables defined in the
    inventory file are used

ucs_storage_local_disk_blade:
    hostname: "{{ucs_ip}}"
    username: "{{ucs_username}}"
    password: "{{ucs_password}}"
    chassis_id: 2
    blade_id: 2, 6
    slot_id: 1
    disk_id: 1, 2
    #disk_state: "unconfigured-good"
    disk_state: "jbod"

'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec

def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(chassis_id=dict(type='str'),
                         blade_id=dict(type='str'),
                         slot_id=dict(type='str'),
                         disk_id=dict(type='str'), 
                         disk_state=dict(type='str', choices=['jbod', 'unconfigured-good']))

    module = AnsibleModule(argument_spec,
                           supports_check_mode=True)
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
        
        num_blades = 1
        blade_list = module.params['blade_id'].split(',')
        blade_id_start = int( blade_list[0] )
        if( len(blade_list) > 1 ):
            num_blades = int( blade_list[1] )

        num_slots = 1
        slot_list = module.params['slot_id'].split(',')
        slot_id_start = int( slot_list[0] )
        if( len(slot_list) > 1 ):
            num_slots = int( slot_list[1] )

        num_disks = 1
        disk_list = module.params['disk_id'].split(',')
        disk_id_start = int( disk_list[0] )
        if( len(disk_list) > 1 ):
            num_disks = int( disk_list[1] )

        for chassis_num in range( chassis_id_start, chassis_id_start + num_chassis ):
            dn_chassis_base = dn_base + '/chassis-' + str( chassis_num )

            for blade_num in range( blade_id_start, blade_id_start + num_blades ):
                dn_blade_base = dn_chassis_base + '/blade-' + str( blade_num )

                for slot_num in range( slot_id_start, slot_id_start + num_slots ):
                    dn_slot_base = dn_blade_base  + '/board/storage-SAS-' + str( slot_num )

                    for disk_num in range( disk_id_start, disk_id_start + num_disks ):
                        dn = dn_slot_base + '/disk-' + str( disk_num ) 

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
