# reads credentials from ~/.my.cnf
mysqldump sdd > ../backups/sdd-$(date --date='-1 day' +%Y-%m-%d).sql