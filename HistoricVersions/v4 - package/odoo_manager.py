#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import proclib

def freebsd_install_all(packagenames):
    proclib.runprog_shareout(['pkg',  'install'] + list(packagenames) )

def Run():
    #verify_root_permissions()
    freebsd_install_all((
            'less',
            'postgresql13-server',
            'postgresql13-client',
            'py37-pip',
            'git',
            'webfonts',
            ))
    freebsd_install_all((
            'libpq-devel',
            'libjpeg-devel',
            'node-less',
            'libxml2-devel',
            'libxslt-devel',
            ))

Run()