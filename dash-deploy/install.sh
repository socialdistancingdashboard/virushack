#!/bin/bash
sudo yum -y -q update
sudo yum install -y git
sudo yum install -y python3
sudo pip3 install dash
cd /usr/bin
sudo curl -O https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/dash-deploy/rundashboard.sh
cd /etc/systemd/system
sudo curl -O https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/dash-deploy/rundashboard.service
sudo chmod 644 /etc/systemd/system/rundashboard.service
sudo systemctl enable rundashboard.service
cd /home/ec2-user
git clone https://github.com/socialdistancingdashboard/frontendv2.git
curl -O https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/dash-deploy/update.sh
sudo chmod u+x update.sh
sudo ./update.sh
sudo chown -R ec2-user:ec2-user /home/ec2-user
sudo systemctl start rundashboard.service
sudo su
crontab -u ec2-user -l
echo -e "*/30 * * * * /home/ec2-user/update.sh >/dev/null 2>&1" | crontab -u ec2-user -
exit
