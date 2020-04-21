#!/bin/bash

if [ "$UID" != 0 ]
then
    echo "Please run as root."
    exit -1
fi

if [ ! -d installer ]
then
    echo "This is meant to be run from installer's parent directory."
    exit -1
fi

mkdir -p /odoo/odoomanager/
sudo cp -Rv * /odoo/odoomanager/
sudo cp installer/odoomanager.service /lib/systemd/system/
sudo systemctl start odoomanager.service
