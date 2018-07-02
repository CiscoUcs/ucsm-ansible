### Ansible Development Notes

ucs_ modules in development follow processes documented at http://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html.  The modules support ansible-doc, and when submitted to Ansible they must pass Ansible CI testing and have integration tests.

When developing ucs_ modules in this repository, here are a few helpful commands to sanity check the code and documentation (replace module_name with your module (e.g., ucs_vlans)).  Ansible modules won't generally be pylint or pycodestyle (PEP8) clean without disabling several of the checks:
  ```
  pylint --disable=invalid-name,no-member,too-many-nested-blocks,redefined-variable-type,too-many-statements,too-many-branches,broad-except,line-too-long,missing-docstring,wrong-import-position,too-many-locals <module_name>.py
  
  pycodestyle --max-line-length 160 --config /dev/null --ignore E402 <module_name>.py
  
  ansible-doc <module_name>
  ```
### Contributing Modules to Ansible
Below is a summary of steps needed for contributing ucs_ modules directly to Ansible (refer to at http://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html for details):
1. Fork the main Ansible repo in your own github account
2. Clone your repo.
3. Setup virtualenv within the cloned repo (see "Envrionment setup" in the development walkthrough linked above):
```
. venv/bin/activitate; . hacking/env-setup
```
4. Create a feature branch.  PRs can only be submitted against one module, so always create a feature branch per PR and only edit one module on the branch at a time:
```
git checkout -b <ucs feature branch name> (e.g., ucs_san_conn_docs)
```
5. Create/edit files in lib/ansible/modules/remote_management/ucs (e.g., ucs_san_connectivity.py).  Also, be sure to look at ACI modules for references on docs/formatting/etc. (e.g., https://github.com/dsoper2/ansible/blob/devel/lib/ansible/modules/network/aci/aci_epg.py )
6. Be sure documentation is part of the module (run locally prior to submitting a PR):
```
ansible-doc <module name> (e.g., ansible-doc ucs_san_connectivity)
```
- See http://docs.ansible.com/ansible/latest/dev_guide/developing_modules_documenting.html#documentation-block and http://docs.ansible.com/ansible/latest/YAMLSyntax.html for documentation help.
6. Run sanity tests on the module (run locally prior to submitting a PR):
```
ansible-test sanity --test pep8 <module name>
ansible-test sanity --test pylint <module name>
ansible-test sanity --test validate-modules <module name>
ansible-test sanity --test no-underscore-variable <module name>
ansible-test sanity --test import --python 2.7 <module name>
ansible-test sanity --test docs-build <module name>
```
- Note that you can append --requirements to any ansible-test line to install required modules
7. Create and run integration tests.  See test/integration/targets/ucs_uuid_pool as an example
- Integration tests can't be run by ansible (since they require ucs resources), but you can create your own integration test config (make sure you don't commit this)
- Here's an example test/integration/integration_config.yml with ucs vars appended:
```
---
win_output_dir: 'C:\ansible_testing'
output_dir: ~/ansible_testing
ucs_hostname: 172.22.250.102
ucs_username: admin
ucs_password: password
```
8. Run your integration test:
```
ansible-test integration <module name>
```
9. Once all documentation is in place, sanity tests are passing, and integration tests are passing you can submit a Pull Request (PR).  Ansible provides a PR template that will help you fill in needed fields.
- Here is an example for the ucs_uuid_pool module: https://github.com/ansible/ansible/pull/41743
10. Once your PR is merged, sync your fork (https://help.github.com/articles/syncing-a-fork/ ) and delete your local feature branch (git branch -d branch_name).
- Ansible help is available on IRC: https://webchat.freenode.net/?channels=ansible-network (several other channels exist for help with Ansible)
