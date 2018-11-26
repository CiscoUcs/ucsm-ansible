[![](https://ucspython.herokuapp.com/badge.svg)](https://ucspython.herokuapp.com)

# ucsm-ansible

* Apache License, Version 2.0 (the "License") 

## News

Ansible 2.5 and later features several UCS modules, and we are working to include more in upcoming releases.  This repo represents the working copy of modules submitted to Ansible or in development for future submission.  This repo can be used to provide UCS Ansible modules before their inclusion in official Ansible releases.

Modules in the library directory are submitted or in development for upcoming Ansible releases.  module_utils/remote_management is the module_utils location for modules being actively maintained.

There is currently not support for scripted install/uninstall to avoid collision with Ansible hosted modules and ongoing maintenance.  
See the install section below for step-by-step install and usage instructions.

Cisco's demo Cloud (dcloud.cisco.com) can be used to test and demo the Ansible modules and corresponding roles.  dCloud provides both a Hardware based environment (https://dcloud2-rtp.cisco.com/content/catalogue?search=unified%20computing%20system ) and an emulated environment (https://dcloud2-sjc.cisco.com/content/catalogue?search=ucs%20programmability ) that can be used with the UCS Ansible modules.

Modules submitted to Ansible are also used in roles now available on Ansible Galaxy: https://galaxy.ansible.com/ciscoucs/ucs

### Current Development Status

| Configuration Category | Configuration Task | Module Name | Status (part of 2.5, Proof of Concept, TBD |
| ---------------------- | ------------------ | ----------- | ------ |
| LAN                    | IP Addresses for KVM Access | ucs_ip_pool | in 2.5 |
|                        | MAC Address Pools  | ucs_mac_pool | in 2.5 |
|                        | VLANs              | ucs_vlans   | in 2.5 |
|                        | vNIC Templates     | ucs_vnic_template | in 2.5 |
|                        | LAN Connectivity Policy | ucs_lan_connectivity | in 2.5 |
|                        | Network Control Policy | ucs_network_control | planned for 2.9    |
|                        | Port Channels      | use ucs_managed_objects | See lan/port_channels at  https://galaxy.ansible.com/ciscoucs/ucs |
| SAN                    | WWNN Pools         | ucs_wwn_pool | in 2.5 |
|                        | WWPN Pools         | ucs_wwn_pool | in 2.5 |
|                        | VSANs              | ucs_vsans   | in 2.5 |
|                        | vHBA Templates     | ucs_vhba_template | in 2.5 |
|                        | SAN Connectivity Policy | ucs_san_connectivity | in 2.5 |
| Server                 | UUID Suffix Pool   | ucs_uuid_pool | in 2.7 |
|                        | Server Pool        | use ucs_managed_objects | See servers/server_pools at  https://galaxy.ansible.com/ciscoucs/ucs |
|                        | Server BIOS Policy | use ucs_managed_objects | See servers/bios_policies at  https://galaxy.ansible.com/ciscoucs/ucs |
|                        | FW/Power/Maintenance Polices | use ucs_managed_objects | See servers/power_policies at  https://galaxy.ansible.com/ciscoucs/ucs |
|                        | Boot Policy        | use ucs_managed_objects | See servers/boot_policies at  https://galaxy.ansible.com/ciscoucs/ucs |
|                        | Service Profile Template | ucs_service_profile_template | in 2.8 |
|                        | Service Profile from Template | ucs_service_profile_from_template | Planned for 2.9 |
|                        | Service Profile assoc/disassoc | ucs_service_profile_association | Planned for 2.9 |
| Admin                  | NTP                | use ucs_managed_objects | See admin/ntp at  https://galaxy.ansible.com/ciscoucs/ucs |
|                        | Timezone           | ucs_timezone | in 2.7 |
| Chassis                | Zoning, Profiles, etc. | see ucs_chassis_ modules | Planned for 2.9 |
| Storage                | Local disk, Profiles, etc. | see ucs_storage_ modules | in 2.8 |
### Ansible Development Notes

See https://github.com/CiscoUcs/ucsm-ansible/blob/master/Development.md for details.

### Install
Ansible must be installed.  You can use pip to install:
```
sudo pip install ansible
```
- If you don't have pip installed, here's how to install pip:
```
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
```
The UCSM Ansible modules depend on the UCSM Python SDK.  Here's how to install the ucsmsdk.
```
sudo pip install ucsmsdk
```
- If you would like the latest ucsmsdk from GitHub, here is an alternate install method:
```
sudo pip install git+https://github.com/CiscoUcs/ucsmsdk.git
```
It is a good idea to verify that the ucsmsdk can connect to the domains you want to manage with Ansible.  Here is an example connection test using python:
```
# python
Python 2.7.14 (default, Apr 27 2018, 14:31:56) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-11)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from ucsmsdk import ucshandle
>>> handle = ucshandle.UcsHandle(ip='172.22.250.236', username='admin', password='password')
>>> handle.login()
True
```
#### Using Ansible modules from this repository
Ansible 2.5 and later include several UCSM modules.  If you need more recent content you can clone and use this repository: 
```
git clone https://github.com/ciscoucs/ucsm-ansible
```
After cloning this repository to a local directory Ansible will find the repo's library directory as a modules path for any playbooks residing in the ucsm-ansible directory.  If Ansible reports that it cannot find a module from the library directory, you will need to specfiy the cloned repository as a library location in your .ansible.cfg file.  Here is .ansible.cfg example content:
```
[defaults]
library = <path to ucsm-ansible clone>/library
```
  
### Example usage
Once Ansible is installed you can create inventory files and playbooks to manage your UCS domains.  Each module supports ansible-doc which includes example usage:
```
# ansible-doc ucs_vlans
<snip>
EXAMPLES:
- name: Configure VLAN
  ucs_vlans:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: vlan2
    id: '2'
    native: 'yes'
```
This repository includes an example inventory file that can be edited with information for the UCSM domain you want to configure:
```
# vi inventory
[ucs]
ucs1 ucs_hostname=192.168.1.1 ucs_username=admin ucs_password=password ucs_state=present
```
An example_playbook.yml playbook is also included to test VLAN configuration on the UCSM domain given in the inventory file:
```
# vi example_playbook.yml 

---
# Example Playbook: VLAN configuration using the [ucs] hosts group
- hosts: ucs
  connection: local
  gather_facts: no
  tasks:
  - name: Configure VLAN
    ucs_vlans:
      hostname: "{{ ucs_hostname }}"
      username: "{{ ucs_username }}"
      password: "{{ ucs_password }}"
      state: "{{ ucs_state }}"
      name: vlan2
      id: '2'
      native: 'no'
```
Ansible will use data from the inventory file for the "{{ ucs_... }}" variables above.  Multiple UCSM domains can be listed in the inventory file and Ansible will configure all the listed domains in parallel using host specific data in place of the "{{ ucs_... }}" variables.

The ansible-playbook command can be used to run the above playbook and inventory file:
```
# ansible-playbook -i inventory example_playbook.yml

PLAY [ucs] *********************************************************************

TASK [Configure VLAN] **********************************************************
changed: [ucs1]

PLAY RECAP *********************************************************************
ucs1                       : ok=1    changed=1    unreachable=0    failed=0   
```

# Community:

* We are on Slack - slack requires registration, but the ucspython team is open invitation to
  anyone to register [here](https://ucspython.herokuapp.com)
