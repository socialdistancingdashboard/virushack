#!/bin/bash
cd /home/ec2-user
/usr/bin/wget -N -q https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/EveryoneCounts.py >/dev/null 2>&1
cd /home/ec2-user/dashboard
/usr/bin/wget -N -q https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/dashboard/__init__.py >/dev/null 2>&1
/usr/bin/wget -N -q https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/dashboard/dashboard.py >/dev/null 2>&1
/usr/bin/wget -N -q https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/dashboard/dashboard_pages.py >/dev/null 2>&1
cd /home/ec2-user
git pull
