#!/bin/bash

# runs all update scripts
/usr/bin/python3 db_upload_corona.py >> cron.log
/usr/bin/python3 db_upload_gmap_popularity.py >> cron.log
/usr/bin/python3 db_upload_energy.py >> cron.log