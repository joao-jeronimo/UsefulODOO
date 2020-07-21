#!/bin/bash

sudo apt update
sudo apt upgrade -y
sudo apt dist-upgrade -y

apt install -y sudo postgresql postgresql-client links wkhtmltopdf less python3-pip openssh-server pwgen git ttf-mscorefonts-installer libpq-dev libjpeg-dev zlib1g-dev node-less libxml2-dev libxslt-dev
apt build-dep -y python-ldap

sudo -H pip3 install --upgrade pip
sudo -H pip3 install --upgrade six pillow python-dateutil pytz
sudo -H pip3 install --ignore-installed pyserial

sudo -H pip3 install xlrd xlwt pyldap qrcode vobject num2words phonenumbers
