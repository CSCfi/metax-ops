# -*- mode: ruby -*-
# vi: set ft=ruby :

# This script is to be run by saying 'vagrant up' in this folder. This script
# should be run only when creating a local development environment.

# Pre-provisioner shell script installs Ansible into the guest and continues
# to provision rest of the system in the guest. Works also on Windows.
$script = <<SCRIPT
set -e
if [ ! -f /vagrant_bootstrap_done.info ]; then
  sudo yum -y update
  sudo yum -y install epel-release libffi-devel openssl-devel git python3-3.6.8 python3-devel-3.6.8
  sudo rpm -U http://opensource.wandisco.com/centos/7/git/x86_64/wandisco-git-release-7-2.noarch.rpm && yum install -y git
  pip3 install ansible
  su --login -c 'cd /metax/ansible && source install_requirements.sh && ansible-playbook site_provision.yml' vagrant
  sudo touch /vagrant_bootstrap_done.info
fi
SCRIPT


required_plugins = %w( vagrant-vbguest )
required_plugins.each do |plugin|
   exec "vagrant plugin install #{plugin};vagrant #{ARGV.join(" ")}" unless Vagrant.has_plugin? plugin || ARGV[0] == 'plugin'
end

Vagrant.configure("2") do |config|
  config.vm.define "metax_local_dev_env_III" do |server|
    server.vm.box = "centos/7"
    server.vm.network :private_network, ip: "50.50.50.50"

    # Basic VM synced folder mount
    server.vm.synced_folder "./metax-api", "/metax/metax-api", :mount_options => ["dmode=777,fmode=777"], create: true
    server.vm.synced_folder "./ansible", "/metax/ansible", :mount_options => ["dmode=775,fmode=775"]

    server.vm.provision "shell", inline: $script

    server.vm.provider "virtualbox" do |vbox|
        vbox.name = "metax_local_development_III"
        vbox.gui = false
        vbox.memory = 2048
        vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
    end
  end
end

