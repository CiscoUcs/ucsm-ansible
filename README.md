
* Apache License, Version 2.0 (the "License") 

# Overview

See https://github.com/CiscoUcs/ucsm-ansible for additional information on installation and usage of the core UCSM modules.  This repository provides example playbooks, inventory, and group_vars files for deployment of several reference UCS environments.

Tested on UCS Manager version 3.1 and later.  Please submit issues for problems found on earlier UCSM versions.

# install
- ansible must be installed
```
sudo pip install ansible
```
- you will need the latest ucsmsdk
```
sudo pip install -U ucsmsdk
```
- you will need the latest ucsm_apis
```
git clone https://github.com/ciscoucs/ucsm_apis
cd ucsm_apis
sudo make install
```
- clone this repository and install the ansible modules
```
git clone https://github.com/dsoper2/ucsm-ansible
cd ucsm-ansible
sudo python install.py
```

# uninstall
```
cd ucsm-ansible
sudo python uninstall.py
```
# Usage Examples

Playbooks, inventory files, and group_vars files are provided for the following environments:
  # Docker Datacenter (part of Docker Enterprise Edition)
  - Playbook: dockerdc.yml
  - Inventory and data files (in the inventory and group_vars directories):
    - docker_ucspe (for use with the UCS Platform Emulator - see https://communities.cisco.com/ucspe for more information)
    - docker_dcloud (for use in the Unified Computing System dCloud demo - see https://dcloud-cms.cisco.com/demo/cisco-ucs-3-1-v1 for more information)
  - Please see the Docker Datacenter Cisco Validated Design for more information on the reference design: http://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/UCS_CVDs/ucs_docker.html
  - Example usage:
```
ansible-playbook -i inventory/docker_ucspe dockerdc.yml
```

  # Kubernetes on UCS Bare Metal (KuBaM!)
  - Playbook: kubam.yml
  - Inventory and data files (in the inventory and group_vars directories):
    - cc7_kubam (for internal Cisco use.  Can be customaized for use in the Unified Computing System dCloud demo - see https://dcloud-cms.cisco.com/demo/cisco-ucs-3-1-v1 for more information)
  - For more information on the KuBaM! reference design please see: https://ciscoucs.github.io/kubam/
  - Example usage:
```
ansible-playbook -i inventory/cc7_kubam kubam.yml
```

  # VMware VSAN with Cisco UCS
  - Playbook: cisco-vsan.yml
  - Inventory and data files (in the inventory and group_vars directories):
    - cisco-vsan (for internal Cisco use.  Can be customaized for use in the Unified Computing System dCloud demo - see https://dcloud-cms.cisco.com/demo/cisco-ucs-3-1-v1 for more information)
  - For more information on the VSAN reference design please see: https://www.cisco.com/c/en/us/solutions/collateral/data-center-virtualization/unified-computing/whitepaper-c11-735680.html?referring_site=RE&pos=1&page=https://www.cisco.com/c/en/us/solutions/collateral/data-center-virtualization/desktop-virtualization-solutions-vmware-horizon-view/whitepaper_C11-732332.html
  - Example usage:
```
ansible-playbook -i inventory/cisco-vsan cisco-vsan.yml
```
  
# Community:

* We are on Slack - slack requires registration, but the ucspython team is open invitation to
  anyone to register [here](https://ucspython.herokuapp.com)
