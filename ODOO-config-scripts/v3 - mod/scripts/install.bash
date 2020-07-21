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

# Generate and prepare a password:
export ODOO_PASSWORD=`pwgen -y -c -n 40 1 --secure | tr -d "\n"`
echo "{'DB_PASSWORD': '$ODOO_PASSWORD'}" > "$SCRIPTCONFIG"

# Install dependencies:
sudo apt update
sudo apt upgrade -y
sudo apt dist-upgrade -y

apt install -y sudo postgresql postgresql-client links wkhtmltopdf less python3-pip openssh-server pwgen git ttf-mscorefonts-installer libpq-dev libjpeg-dev zlib1g-dev node-less libxml2-dev libxslt-dev
apt build-dep -y python3-ldap

sudo -H pip3 install --upgrade pip
sudo -H pip3 install --upgrade six pillow python-dateutil pytz
sudo -H pip3 install --ignore-installed pyserial

sudo -H pip3 install xlrd xlwt pyldap qrcode vobject num2words phonenumbers

# Clone Odoo repository:
cd "$ODOOMAN_DIR"/
git clone "$MAIN_GIT_REMOTE_REPO" "$MAIN_GIT_LOCAL_REPO"

# Create "$ODOO_USERNAME" user:
sudo useradd -d "$ODOOMAN_DIR"/ "$ODOO_USERNAME"

######################################
# Setup Odoo Manager:
######################################
# Clone the 13 version from the main tree:
git clone --single-branch -b "$ODOOMAN_ODOO_REL" "$MAIN_GIT_LOCAL_REPO" "$RELEASES_DIR"/"$ODOOMAN_ODOO_REL"
# Install the config file:
# TODO!
# Install the systemd script:
# TODO!

######################################
# Fix permissions:
######################################
sudo chown "$ODOO_USERNAME:$ODOO_USERNAME" -Rc "$ODOOMAN_DIR"/
sudo chmod ug+rw,o-rwx -Rc "$ODOOMAN_DIR"/
sudo find "$ODOOMAN_DIR"/ -type d -exec chmod ug+x {} \;

sudo usermod -aG "$ODOO_USERNAME" "$USER"

unset ODOO_PASSWORD
