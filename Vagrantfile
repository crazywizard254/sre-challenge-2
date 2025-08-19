Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.ssh.insert_key = true
  config.vm.network "private_network", ip: "192.168.56.10"
    config.vm.network "forwarded_port", guest: 8080, host: 8080, host_ip: "0.0.0.0", auto_correct: true
    config.vm.network "forwarded_port", guest: 8025, host: 8025, host_ip: "0.0.0.0", auto_correct: true   # MailHog web UI
    config.vm.network "forwarded_port", guest: 1025, host: 1025, host_ip: "0.0.0.0", auto_correct: true   # MailHog SMTP port
  config.vm.provider "virtualbox" do |vb|
    vb.memory = 2048
    vb.cpus = 2
  end
  config.vm.provision "shell", path: "provision.sh"
end
