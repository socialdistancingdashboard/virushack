#!/bin/bash
sudo apt update
sudo apt upgrade
sudo apt -y install python3-pip

sudo pip3 install pandas
sudo pip3 install streamlit
pip3 install pandas
pip3 install streamlit

sudo reboot

cd /home/ubuntu/
wget https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/virushack_dashboard.py

