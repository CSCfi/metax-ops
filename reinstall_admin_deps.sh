rm -rf ansible/inventories/staging
rm -rf ansible/inventories/production
unzip metax_ops_sec.zip
rm -rf ansible/roles/ansible-elasticsearch
cd ansible
source install_requirements.sh
