#!/bin/bash

############################
### Vars:
export ODOOMAN_DIR="/odoo"
export ODOOMAN_ODOO_REL="13.0"

export MAIN_GIT_REMOTE_REPO="https://github.com/odoo/odoo.git"
export MAIN_GIT_LOCAL_REPO="$ODOOMAN_DIR"/odoo-full-git
export SCRIPTCONFIG="$ODOOMAN_DIR"/odooconfig.conf
export RELEASES_DIR="$ODOOMAN_DIR"/releases
export ODOO_USERNAME="odoo"

export WKHTMLTOPDF_VERSION="0.12.6-1"

############################
function die () {
  local message=$1
  [ -z "$message" ] && message="Died"
  echo "$message (at ${BASH_SOURCE[1]}:${FUNCNAME[1]} line ${BASH_LINENO[0]}.)" >&2
  exit 1
}

############################
if [ "$UID" != 0 ]
then
    echo "Please run as root."
    exit -1
fi

grep -o -Hnr "deb-src" /etc/apt/sources.list*
if [ "$?" != 0 ]
then
    echo "Please add source repositories to sources.list file."
    exit -1
fi


# Prepare /odoo/ subdirectories:
mkdir "$ODOOMAN_DIR"/
mkdir "$ODOOMAN_DIR"/configs/
mkdir "$ODOOMAN_DIR"/logs/
mkdir "$RELEASES_DIR"/
mkdir "$ODOOMAN_DIR"/manager_mods

# Install dependencies:
sudo apt update || die
sudo apt upgrade -y || die
sudo apt dist-upgrade -y || die

apt install -y sudo links less openssh-server || die
apt install -y postgresql postgresql-client || die
apt install -y python3-pip pwgen git ttf-mscorefonts-installer libpq-dev libjpeg-dev node-less libxml2-dev libxslt-dev || die
apt install -y zlib1g-dev || die
apt build-dep -y python3-ldap || die

# Install correct wkhtmltopdf version:
pushd ~
wget -c https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_"$WKHTMLTOPDF_VERSION".focal_amd64.deb || die
sudo dpkg -i wkhtmltox_"$WKHTMLTOPDF_VERSION".focal_amd64.deb || die
sudo apt --fix-broken install || die
popd

sudo -H pip3 install --upgrade pip || die
sudo -H pip3 install --upgrade six pillow python-dateutil pytz || die
sudo -H pip3 install --ignore-installed pyserial psycopg2-binary || die
sudo -H pip3 install --upgrade unidecode || die    # For SEPA modules

sudo -H pip3 install xlrd xlwt pyldap qrcode vobject num2words phonenumbers || die

# Clone Odoo repository:
cd "$ODOOMAN_DIR"/
git clone "$MAIN_GIT_REMOTE_REPO" "$MAIN_GIT_LOCAL_REPO" || die

# Create "$ODOO_USERNAME" user:
sudo useradd -d "$ODOOMAN_DIR"/ "$ODOO_USERNAME"

######################################
# Setup Odoo Manager:
######################################
# Clone the 13 version from the main tree:
pushd "$MAIN_GIT_LOCAL_REPO"
git checkout "$ODOOMAN_ODOO_REL" || die
popd
git clone --single-branch -b "$ODOOMAN_ODOO_REL" "$MAIN_GIT_LOCAL_REPO" "$RELEASES_DIR"/"$ODOOMAN_ODOO_REL" || die
# Install version-specific deps:
cd "$RELEASES_DIR"/"$ODOOMAN_ODOO_REL"
sudo -H pip3 install -r requirements.txt || die

# Put modules in their place:
cp -Rv ../manager_mods/* /odoo/manager_mods/

# Install the config file:
cat << EOF > "$ODOOMAN_DIR"/configs/odooman.conf
[options]
addons_path = $RELEASES_DIR/$ODOOMAN_ODOO_REL/addons,$ODOOMAN_DIR/manager_mods
#admin_passwd =
csv_internal_sep = ,
data_dir = /odoo/.local/share/Odoo
# Use unix sockets with no password:
#db_host = localhost
#db_port = 5432
#db_password = $ODOO_PASSWORD
db_maxconn = 64
db_name = odooman
db_sslmode = prefer
db_template = template1
db_user = $ODOO_USERNAME
demo = {}
email_from = False
;geoip_database = /usr/share/GeoIP/GeoLite2-City.mmdb
http_enable = True
http_interface = 0.0.0.0
http_port = 8000
import_partial = 

#limit_memory_hard = 2684354560
limit_memory_hard = 5368709120
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
EOF

# Install the systemd script:
cat << EOF > "/lib/systemd/system/odoomanager.service"
[Unit]
Description=OdooManager
After=network.target

[Service]
Type=simple
User=$ODOO_USERNAME
Group=$ODOO_USERNAME
ExecStart=$RELEASES_DIR/$ODOOMAN_ODOO_REL/odoo-bin --database=odooman --db-filter="odooman" --config $ODOOMAN_DIR/configs/odooman.conf --logfile /odoo/logs/odoomanager.log
KillMode=mixed

[Install]
WantedBy=multi-user.target
EOF

######################################
# Setup PostgreSQL:
######################################
# Create the user:
sudo -u postgres bash -c "createuser -s $ODOO_USERNAME"
# Set the password:


######################################
# Fix permissions:
######################################
sudo chown "$ODOO_USERNAME:$ODOO_USERNAME" -Rc "$ODOOMAN_DIR"/
sudo chmod ug+rw,o-rwx -Rc "$ODOOMAN_DIR"/
sudo find "$ODOOMAN_DIR"/ -type d -exec chmod ug+sx -c {} \;

sudo usermod -aG "$ODOO_USERNAME" "$USER"

unset ODOO_PASSWORD

echo "================================="
echo "======= Installation Done ======="
echo "================================="
echo ""
echo "== Known Caveats:"
echo "Error: psycopg2.errors.InvalidParameterValue: new encoding (UTF8) is incompatible with the encoding of the template database (SQL_ASCII)"
echo "https://stackoverflow.com/questions/16736891/pgerror-error-new-encoding-utf8-is-incompatible"
echo ""
#######################################
echo "== Falta fazer:"
echo "odoo    ALL=(ALL) NOPASSWD:/odoo/manager/catinto"
echo "# Criar ficheiro /odoo/manager/catinto"
echo "   #!/bin/bash
echo "   export INSTANCENAME="$1""
echo "   cat > /lib/systemd/system/odoo-"$INSTANCENAME".service"
echo ""
echo "# Falta securizar este ficheiro: não deverá deixar sobre-escrever ficheiros existentes..."
