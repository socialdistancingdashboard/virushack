#!/bin/bash
sudo yum -y -q update
sudo yum install -y python3
sudo pip3 install pandas
sudo pip3 install streamlit
cd /home/ec2-user
curl -O https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/EveryoneCounts.py
cd /usr/bin
sudo curl -O https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/streamlit-beanstalk/rundashboard.sh
cd /etc/systemd/system
sudo curl -O https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/streamlit-beanstalk/rundashboard.service
sudo chmod 644 /etc/systemd/system/rundashboard.service
sudo systemctl enable rundashboard.service
sudo systemctl start rundashboard.service
cd /home/ec2-user
mkdir dashboard
curl -O https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/streamlit-beanstalk/update.sh
chmod u+x update.sh
echo  -e  "$(crontab -l)\n*/30 * * * * /home/ec2-user/update.sh >/dev/null 2>&1" | crontab -
