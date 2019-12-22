#!/usr/bin/python3
# -*- coding: utf8 -*-

# Documentation:
#  * First thing to do is to ad a swapfile, unless your system has 2GB of RAM.

import os
import os.path
import proclib

# Parameters:
INSTANCENAME    = "verdoo"
THEBRANCH       = "13.0"
MAIN_GIT_REMOTE_REPO    = "https://github.com/odoo/odoo.git"
MAIN_GIT_LOCAL_REPO     = "/odoo/odoo-full-git/"

# Facts of the universe:
ODOO_USERNAME = "odoo"


def createdirs():
    try:
        os.mkdir("/odoo/")
    except FileExistsError:
        pass
    try:
        os.mkdir("/odoo/configs/")
    except FileExistsError:
        pass
    try:
        os.mkdir("/odoo/logs/")
    except FileExistsError:
        pass

def installpackages():
    os.chdir("/odoo/")
    proclib.runprog_shareout(["sudo", "apt", "update"])
    proclib.runprog_shareout(["sudo", "apt", "upgrade", "-y"])
    proclib.runprog_shareout(["sudo", "apt", "dist-upgrade", "-y"])
    
    proclib.runprog_shareout(["apt", "install", "-y", "sudo", "postgresql", "postgresql-client", "links", "wkhtmltopdf", "less", "python3-pip", "openssh-server", "pwgen", "git", "ttf-mscorefonts-installer", "libpq-dev", "libjpeg-dev", "zlib1g-dev", "node-less", "libxml2-dev", "libxslt-dev"])
    proclib.runprog_shareout(["apt", "build-dep", "-y", "python-ldap"])
    
    proclib.runprog_shareout(["sudo", "-H", "pip3", "install", "--upgrade", "pip"])
    #proclib.runprog_shareout(["sudo", "-H", "pip3", "install", "--upgrade", "six", "pillow", "python-dateutil", "pytz"])
    #proclib.runprog_shareout(["sudo", "-H", "pip3", "install", "--ignore-installed", "pyserial"])
    proclib.runprog_shareout(["sudo", "-H", "pip3", "install", "xlrd", "xlwt", "pyldap", "qrcode", "vobject", "num2words", "phonenumbers"])

def installdeps(the_branch):
    os.chdir(branch_path(the_branch))
    proclib.runprog_shareout(["sudo", "-H", "pip3", "install", "-r", "requirements.txt"])

def createusers():
    proclib.runprog_shareout(["useradd",    "--no-create-home",
                                            "--base-dir", "/odoo/",
                                            "--home-dir", "/odoo/",
                                            "--shell", "/bin/false",
                                            ODOO_USERNAME])
    #su postgres -c "createuser odoo"
    proclib.runprog_shareout(["su", "postgres", "-c", "createuser -s "+ODOO_USERNAME])

# Main ODOO source:
def gitclone():
    os.chdir("/odoo/")
    proclib.runprog_shareout(["git", "clone", MAIN_GIT_REMOTE_REPO, MAIN_GIT_LOCAL_REPO])
def gitcloned():
    return os.path.isdir(MAIN_GIT_LOCAL_REPO)

# ODOO release branches:
def clonebranch(the_branch):
    proclib.runprog_shareout(["git", "clone", "-b", the_branch, "--single-branch", MAIN_GIT_LOCAL_REPO, branch_path(the_branch)])
def branchcloned(the_branch):
    return os.path.isdir(branch_path(the_branch))
def branch_path(the_branch):
    return "/odoo/releases/odoo-b%s/"%(the_branch,)

# Odoo config file:
def create_config_file(instance_name):
    config_file_template = """[options]
addons_path =  %(branchpath)s/addons
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
http_port = 8070
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
    configfile_concrete = config_file_template % {  'branchpath': branch_path(THEBRANCH),
                                                    'instancename': instance_name,
                                                    'odoo_username': ODOO_USERNAME, }
    configfile_obj = open(odoo_configfile_path(instance_name), "w")
    configfile_obj.write(configfile_concrete)
    configfile_obj.close()
def odoo_configfile_path(instance_name):
    return ("/odoo/configs/odoo-%s.conf"%instance_name)
    #return ("/etc/systemd/system/multi-user.target.wants/odoo-%s.service"%instance_name)

# Systemd scripts:
def is_instance_installed(instance_name):
    return os.path.isfile(systemd_configfile_path(instance_name))
def create_systemd_config(instance_name):
    systemd_file_template = """
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
    configfile_concrete = systemd_file_template % { 'branchpath': branch_path(THEBRANCH),
                                                    'instancename': instance_name,
                                                    'odoo_username': ODOO_USERNAME, }
    configfile_obj = open(systemd_configfile_path(instance_name), "w")
    configfile_obj.write(configfile_concrete)
    configfile_obj.close()
def systemd_configfile_path(instance_name):
    return ("/lib/systemd/system/odoo-%s.service"%instance_name)
    #return ("/etc/systemd/system/multi-user.target.wants/odoo-%s.service"%instance_name)

def fixperms():
    proclib.runprog_shareout(["sudo", "chown", "odoo:odoo", "-R", "/odoo/"])


def main():
    createdirs()
    installpackages()
    createusers()
    
    if not gitcloned():
        gitclone()
    if not is_instance_installed(INSTANCENAME):
        # Fetch the odoo source:
        # Clone the desired release branch:
        if not branchcloned(THEBRANCH):
            clonebranch(THEBRANCH)
            installdeps(THEBRANCH)
        create_config_file(INSTANCENAME)
        create_systemd_config(INSTANCENAME)
    fixperms()
    print("Start this instance with command:\n" +
          "sudo systemctl start odoo-"+INSTANCENAME)

main()
