# -*- mode: ruby -*-
# vi: set ft=ruby :


# Pre-provisioner shell script installs Ansible into the guest and continues
# to provision rest of the system in the guest. Works also on Windows.
$script = <<SCRIPT
if [ ! -f /vagrant_bootstrap_done.info ]; then
  export DEBIAN_FRONTEND=noninteractive
  sudo apt-get update
  sudo apt-get upgrade
  #CENTOS: sudo apt-get -y install epel-release
  #CENTOS: sudo apt-get -y upgrade ca-certificates --disablerepo=epel
  sudo apt-get -y install python-pip gcc libffi-dev libssl-dev python-dev
  sudo pip install pip --upgrade
  sudo pip install setuptools --upgrade
  sudo pip install markupsafe ansible paramiko
  sudo pip install urllib3
  sudo pip install pyopenssl
  sudo pip install ndg-httpsclient
  sudo pip install pyasn1
  sudo touch /vagrant_bootstrap_done.info
fi
cd /metax/ansible
ansible-playbook site.yml
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.define "metax_local_dev_env" do |server|
    #CENTOS: server.vm.box = "centos-7"
    #CENTOS: server.vm.box_url = "http://cloud.centos.org/centos/7/vagrant/x86_64/images/CentOS-7-x86_64-Vagrant-1703_01.VirtualBox.box"
    server.vm.box = "ubuntu/xenial64"

    server.vm.network :private_network, ip: "20.20.20.20"

    case RUBY_PLATFORM
    when /mswin|msys|mingw|cygwin|bccwin|wince|emc/
        # Fix Windows file rights, otherwise Ansible tries to execute files
        server.vm.synced_folder "./", "/metax", :mount_options => ["dmode=755","fmode=644"]
    else
        # Basic VM synced folder mount
        server.vm.synced_folder "", "/metax"
    end

    server.vm.provision "shell", inline: $script

    server.vm.provider "virtualbox" do |vbox|
        vbox.name = "metax_local_development"
        vbox.gui = false
        vbox.memory = 2048
        vbox.customize ["modifyvm", :id, "--nictype1", "virtio"]
    end
  end
end
