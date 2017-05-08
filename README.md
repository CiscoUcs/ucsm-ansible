# ucsm-ansible

# install
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

# uninstall
```
cd ucsm-ansible
sudo python uninstall.py
```

