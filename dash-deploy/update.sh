#!/bin/bash
cd /home/ubuntu/frontendv2
git fetch --all && git checkout --force "origin/master"
secrethub inject -i config.json.tpl -o config.json --identity-provider=aws --force
cd cache
rm *
sudo systemctl restart rundashboard.service
