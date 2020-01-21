#!/usr/bin/python3
# -*- coding: utf8 -*-
import pudb
import os
import proclib
from taskman import *

MAIN_GIT_REMOTE_REPO    = "https://github.com/odoo/odoo.git"
MAIN_GIT_LOCAL_REPO     = "/odoo/odoo-full-git/"
SCRIPTCONFIG            = "/odoo/odooconfig.conf"
ODOO_USERNAME           = "odoo"

ODOO_CONFIGFILE_TEMPLATE = """[options]
addons_path = %(branchpath)s/addons
#admin_passwd =
csv_internal_sep = ,
data_dir = /odoo/.local/share/Odoo
db_host = localhost
db_maxconn = 64
db_name = %(instancename)s
db_password = 
db_port = 5432
db_sslmode = prefer
db_template = template1
db_user = %(odoo_username)s
demo = {}
email_from = False
;geoip_database = /usr/share/GeoIP/GeoLite2-City.mmdb
http_enable = True
http_interface = 0.0.0.0
http_port = %(httpport)s
import_partial = 
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 60
limit_time_real = 120
limit_time_real_cron = -1
list_db = True
log_db = False
log_db_level = warning
log_handler = :INFO
log_level = info
logrotate = False
longpolling_port = 8072
max_cron_threads = 2
osv_memory_age_limit = 1.0
osv_memory_count_limit = False
pg_path = None
pidfile = False
proxy_mode = True
reportgz = False
server_wide_modules = web
smtp_password = False
smtp_port = 25
smtp_server = localhost
smtp_ssl = False
smtp_user = False
syslog = False
test_commit = False
test_enable = False
test_file = False
test_report_directory = False
translate_modules = ['all']
unaccent = False
without_demo = True
workers = 0
"""


SYSTEMD_FILE_TEMPLATE = """
[Unit]
Description=Odoo-instance-%(instancename)s
After=network.target

[Service]
Type=simple
User=%(odoo_username)s
Group=%(odoo_username)s
ExecStart=%(branchpath)s/odoo-bin --database=%(instancename)s --db-filter="%(instancename)s.*" --config /odoo/configs/odoo-%(instancename)s.conf --logfile /odoo/logs/odoo-%(instancename)s.log --init=base
KillMode=mixed

[Install]
WantedBy=multi-user.target
"""
