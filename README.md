[![](https://ucspython.herokuapp.com/badge.svg)](https://ucspython.herokuapp.com)

# ucsm-ansible

* Apache License, Version 2.0 (the "License") 

## News

Ansible 2.5 will ship with several UCS modules and we are working to include more in upcoming releases.  This repo represents the working copy of modules submitted to Ansible or in development for future submission.

Modules in the library directory that are prefixed with ucs (and not cisco) are submitted or in development.  utils/remote_management is the module_utils location.

There is currently not support for scripted install/uninstall to avoid collision with Ansible hosted modules and ongoing maintenance.  You can specfiy this repo as a library and module_utils location with env variables or command line options (e.g., ANSIBLE_LIBRARY=./library ANSIBLE_MODULE_UTILS=./utils ansible-playbook ..).

Modules submitted to Ansible are also used in roles now available on Ansible Galaxy: https://galaxy.ansible.com/list#/roles?autocomplete=ucs

### Current Development Status

| Configuration Category | Configuration Task | Module Name | Status (part of 2.5, Proof of Concept, TBD |
| ---------------------- | ------------------ | ----------- | ------ |
| LAN                    | IP Addresses for KVM Access | ucs_ip_pool | in 2.5 |
|                        | MAC Address Pools  | ucs_mac_pool | in 2.5 |
|                        | VLANs              | ucs_vlans   | in 2.5 |
|                        | vNIC Templates     | ucs_vnic_template | in 2.5 |
|                        | LAN Connectivity Policy | ucs_lan_connectivity | in 2.5 |
|                        | Network Control Policy | TBD     | TBD    |
|                        | Port Channels      | TBD         | PoC: see https://github.com/dsoper2/ucsm-ansible |
| SAN                    | WWNN Pools         | ucs_wwn_pool | in 2.5 |
|                        | WWPN Pools         | ucs_wwn_pool | in 2.5 |
|                        | VSANs              | ucs_vsans   | in 2.5 |
|                        | vHBA Templates     | ucs_vhba_template | in 2.5 |
|                        | SAN Connectivity Policy | ucs_san_connectivity | in 2.5 |
| Server                 | UUID Suffix Pool   | ucs_uuid_pool | Planned for 2.6 |
|                        | Server Pool        | TBD         | PoC: see https://github.com/dsoper2/ucsm-ansible |
|                        | Server BIOS Policy | TBD         | PoC: see https://github.com/dsoper2/ucsm-ansible |
|                        | FW/Power/Maintenance Polices | TBD | TBD  |
|                        | Boot Policy        | TBD         | PoC: see https://github.com/dsoper2/ucsm-ansible |
|                        | Service Profile Template | ucs_service_profile_template | Planned for 2.6 |
|                        | Service Profile from Template | ucs_service_profile_from_template | Planned for 2.6 |
|                        | Service Profile assoc/disassoc | ucs_service_profile_association | Planned for 2.6 |
| Admin                  | NTP                | TBD         | PoC: cisco_ucs_ntp module |

# Previously provided install/uninstall instructions for modules prefixed with cisco that are not part of Ansible 2.5

### install
- ansible must be installed
```
sudo pip install ansible
```
- you will need the latest ucsmsdk.
```
git clone https://github.com/ciscoucs/ucsmsdk
cd ucsmsdk
sudo make install
```
- you will need the latest ucsm_apis.
```
git clone https://github.com/ciscoucs/ucsm_apis
cd ucsm_apis
sudo make install
```
- clone this repository and install the ansible modules
```
git clone https://github.com/ciscoucs/ucsm-ansible
cd ucsm-ansible
sudo python install.py
```

### uninstall
```
cd ucsm-ansible
sudo python uninstall.py
```

# Community:

* We are on Slack - slack requires registration, but the ucspython team is open invitation to
  anyone to register [here](https://ucspython.herokuapp.com)
