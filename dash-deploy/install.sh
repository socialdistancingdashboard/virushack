#!/bin/bash
sudo touch /etc/apt/sources.list.d/secrethub.list
echo 'deb [trusted=yes] https://apt.secrethub.io stable main' | sudo tee -a /etc/apt/sources.list.d/secrethub.list
sudo apt-get update -y
sudo apt install -y secrethub-cli
sudo apt install -y secrethub-cli
sudo apt install -y git
sudo apt install -y python3
sudo apt install -y python3-devel
sudo apt install -y gcc
sudo apt install -y python3-pip
sudo apt install -y libspatialindex-dev
sudo pip3 install pandas dash geopandas geopy influxdb_client Flask-Caching rtree
cd /usr/bin
sudo curl -O https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/dash-deploy/rundashboard.sh
cd /etc/systemd/system
sudo curl -O https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/dash-deploy/rundashboard.service
sudo chmod 644 /etc/systemd/system/rundashboard.service
sudo systemctl enable rundashboard.service
cd /home/ubuntu
git clone https://github.com/socialdistancingdashboard/frontendv2.git
curl -O https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/dash-deploy/update.sh
sudo chmod u+x update.sh
sudo ./update.sh
sudo chown -R ubuntu:ubuntu /home/ubuntu
sudo systemctl start rundashboard.service
sudo su
crontab -u ubuntu -l
echo -e "*/30 * * * * /home/ubuntu/update.sh >/dev/null 2>&1" | crontab -u ubuntu -
exit
