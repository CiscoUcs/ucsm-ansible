[![](https://ucspython.herokuapp.com/badge.svg)](https://ucspython.herokuapp.com)

# ucsm-ansible

* Apache License, Version 2.0 (the "License") 

## News

Ansible 2.5 will ship with several UCS modules and we are working to include more in upcoming releases.  This repo represents the working copy of modules submitted to Ansible or in development for future submission.

Modules in the library directory that are prefixed with ucs (and not cisco) are submitted or in development.  utils/remote_management is the module_utils location.

There is currently not support for scripted install/uninstall to avoid collision with Ansible hosted modules and ongoing maintenance.  You can specfiy this repo as a library and module_utils location with env variables or command line options (e.g., ANSIBLE_LIBRARY=./library ANSIBLE_MODULE_UTILS=./utils ansible-playbook ..)

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
