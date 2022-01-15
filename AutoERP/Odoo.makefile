###############################################
### Dependencies to run this on Debian/Ubuntu:
# sudo apt install make git screenie
### To invoke:
# sudo make -f Makefile.mak
# Note - This make file is designed to be ran as:
#  * Regular user in odoo group? No! Directories like /odoo/config are supposed to be only odoo-user written.
#  * By the odoo user? No! Only python should be ran under the odoo user.
#  * By root? Yes. Caller is supposed to reset the permissions after calling the makefile.

#ODOO_FETCH_FULL = yes

############################
### Vars:
ifeq ($(ODOO_REL),)
$(error Var ODOO_REL not defined.)
endif
ifeq ($(INSTANCENM),)
$(error Var INSTANCENM not defined.)
endif
ifeq ($(HTTPPORT),)
$(error Var HTTPPORT not defined.)
endif
ifeq ($(WKHTMLTOPDF_VERSION),)
$(error Var WKHTMLTOPDF_VERSION not defined.)
endif
ifeq ($(INSTANCE_MODFOLDERS),)
$(error Var INSTANCE_MODFOLDERS not defined.)
endif
ifeq ($(PYTHON_MAJOR_VERSION),)
$(error Var PYTHON_MAJOR_VERSION not defined.)
endif
ifeq ($(PYTHON_MINOR_VERSION),)
$(error Var PYTHON_MINOR_VERSION not defined.)
endif
ifeq ($(PYTHONLIBS_DIR),)
$(error Var PYTHONLIBS_DIR not defined.)
endif

ifeq ($(DISTRO),)
$(error Var DISTRO not defined.)
endif
ifeq ($(DEBIAN_CODENAME),)
$(error Var DEBIAN_CODENAME not defined.)
endif

# Example var assignments for bash:
#export ODOO_REL=13.0
#export INSTANCENM=base13
#export HTTPPORT=4083
#export WKHTMLTOPDF_VERSION=0.12.6-1
#export DEBIAN_CODENAME=buster

############################
### Constants:
SHELL = /bin/bash
VIRTUALENV_BIN = pyvenv
ODROOT=/odoo
MAIN_GIT_REMOTE_REPO=https://github.com/odoo/odoo.git
ODOO_USERNAME=odoo
SYSTEMD_PATH=/lib/systemd/system
VIRTUALENV_NAME=Env_Python$(PYTHON_MAJOR_VERSION).$(PYTHON_MINOR_VERSION)_Odoo$(ODOO_REL)
VIRTUALENV_PATH=$(ODROOT)/VirtualEnvs/$(VIRTUALENV_NAME)
VHOST_NAME=$(INSTANCENM)-sidil
VHOST_CONFIG_FILE=/etc/nginx/sites-available/$(VHOST_NAME)
############################
### Sedable versions of args:
SEDABLE_ODROOT:=$(subst /,\/,$(ODROOT))
SEDABLE_INSTANCE_MODFOLDERS:=$(subst /,\/,$(INSTANCE_MODFOLDERS))
SEDABLE_PYTHONLIBS_DIR:=$(subst /,\/,$(PYTHONLIBS_DIR))
SEDABLE_VIRTUALENV_PATH:=$(subst /,\/,$(VIRTUALENV_PATH))

############################
prepare_all:	 	prepare_$(INSTANCENM)
prepare_virtualenv:	$(VIRTUALENV_PATH)


prepare_$(INSTANCENM):  $(SYSTEMD_PATH)/odoo-$(INSTANCENM).service

##########################################################################
### Odoo installation targets: ###########################################
##########################################################################
$(SYSTEMD_PATH)/odoo-$(INSTANCENM).service:  | $(ODROOT)/configs/odoo-$(INSTANCENM).conf $(ODROOT)/stages/dep_branch_requirements $(ODROOT)/stages/dep_wkhtmltopdf $(ODROOT)/stages/system_user_created $(ODROOT)/logs
	@echo "Installing SystemD config file $@..."
	@sed 's/INSTANCENM/$(INSTANCENM)/g;s/ODOO_USERNAME/$(ODOO_USERNAME)/g;s/ODOO_REL/$(ODOO_REL)/g;s/ODROOT/$(SEDABLE_ODROOT)/g;s/PYTHONLIBS_DIR/$(SEDABLE_PYTHONLIBS_DIR)/g;s/VIRTUALENV_PATH/$(SEDABLE_VIRTUALENV_PATH)/g' template.service > "$@"

$(ODROOT)/configs/odoo-$(INSTANCENM).conf:  | $(ODROOT)/releases/$(ODOO_REL) $(ODROOT)/configs $(ODROOT)/stages/sql_user_created
	@echo "Installing config file $@..."
	@sed 's/INSTANCENM/$(INSTANCENM)/g;s/ODOO_USERNAME/$(ODOO_USERNAME)/g;s/LISTEN_ON/$(LISTEN_ON)/g;s/ODOO_REL/$(ODOO_REL)/g;s/ODROOT/$(SEDABLE_ODROOT)/g;s/HTTPPORT/$(HTTPPORT)/g;s/INSTANCE_MODFOLDERS/$(SEDABLE_INSTANCE_MODFOLDERS)/g' template.conf > "$@"

ifeq ($(ODOO_FETCH_FULL),yes)

$(ODROOT)/releases/$(ODOO_REL): | prepare_odoo_fetch $(ODROOT)/releases
	@echo "Fetching $(ODOO_REL) branch..."
	@git clone -b $(ODOO_REL) --single-branch $(ODROOT)/odoo-full-git $@

prepare_odoo_fetch:	$(ODROOT)/odoo-full-git
	@echo "Checking out $(ODOO_REL) branch..."
	@cd $(ODROOT)/odoo-full-git ; git checkout $(ODOO_REL)
	@cd $(ODROOT)/odoo-full-git ; git pull --all
	@cd $(ODROOT)/odoo-full-git ; git pull

endif

ifneq ($(ODOO_FETCH_FULL),yes)

$(ODROOT)/releases/$(ODOO_REL): | $(ODROOT)/releases
	@echo "Fetching $(ODOO_REL) branch..."
	@git clone -b $(ODOO_REL) --single-branch "$(MAIN_GIT_REMOTE_REPO)" $@

endif

$(ODROOT)/odoo-full-git:   | $(ODROOT) $(ODROOT)/stages/dep_git_deb
	@echo "Fetching Odoo source from git"
	@git clone "$(MAIN_GIT_REMOTE_REPO)" $@

$(ODROOT):
	mkdir -p $@
$(ODROOT)/releases $(ODROOT)/configs $(ODROOT)/logs $(ODROOT)/stages $(ODROOT)/python-packages:  | $(ODROOT)
	mkdir -p $@

##########################################################################
### Permissions and env config: ##########################################
##########################################################################
$(ODROOT)/stages/sql_user_created:	| $(ODROOT)/stages $(ODROOT)/stages/dep_apt_packages
	sudo -u postgres bash -c "createuser -s $(ODOO_USERNAME)"
	@touch $@
$(ODROOT)/stages/system_user_created:	| $(ODROOT)/stages
	useradd -d $(ODROOT) $(ODOO_USERNAME)
	@touch $@

$(VIRTUALENV_PATH):
	sudo apt-get install python$(PYTHON_MAJOR_VERSION)
	sudo apt-get install python$(PYTHON_MAJOR_VERSION)-pip python$(PYTHON_MAJOR_VERSION).$(PYTHON_MINOR_VERSION)-venv
	sudo -H pip3 install --upgrade pip
	#$(VIRTUALENV_BIN) --python=/usr/bin/python$(PYTHON_MAJOR_VERSION).$(PYTHON_MINOR_VERSION) $(VIRTUALENV_PATH)
	python$(PYTHON_MAJOR_VERSION).$(PYTHON_MINOR_VERSION) -m venv $(VIRTUALENV_PATH)

##########################################################################
### Dependencies installation: ###########################################
##########################################################################
$(ODROOT)/stages/dep_git_deb:	| $(ODROOT)/stages
	sudo apt-get install git
	@touch $@
$(ODROOT)/stages/dep_branch_requirements:	| $(ODROOT)/stages $(ODROOT)/stages/dep_apt_packages $(ODROOT)/stages/dep_pip_packages
	source $(VIRTUALENV_PATH)/bin/activate && cd $(ODROOT)/releases/$(ODOO_REL) ; pip3 install -r requirements.txt
	source $(VIRTUALENV_PATH)/bin/activate && pip3 install --upgrade num2words
	# Dependencies for the deploy scripts:
	source $(VIRTUALENV_PATH)/bin/activate && pip3 install pymssql odoo-import-export-client odoo-client-lib ezodf gitpython
$(ODROOT)/stages/dep_pip_packages:	| $(ODROOT)/stages $(ODROOT)/stages/dep_apt_packages
	sudo -H pip3 install --upgrade pip
	source $(VIRTUALENV_PATH)/bin/activate && pip3 install --upgrade six pillow python-dateutil pytz unidecode xlutils sqlparse
	source $(VIRTUALENV_PATH)/bin/activate && pip3 install --ignore-installed pyserial
	# Force install PortgreSQL API (psycopg2) from source:
	source $(VIRTUALENV_PATH)/bin/activate && pip3 install --ignore-installed --no-binary :all: psycopg2
	
$(ODROOT)/stages/dep_apt_packages:	| $(ODROOT)/stages/added_deb_repos $(ODROOT)/stages
	apt-get update
	apt-get install -y python3-pip
	apt-get install -y libffi-dev
	apt-get install -y postgresql postgresql-client
	apt-get install -y ttf-mscorefonts-installer fonts-lato node-less
	apt-get install -y libpq-dev libjpeg-dev libxml2-dev libxslt-dev zlib1g-dev
	apt-get build-dep -y python3-ldap python3-lxml python3-greenlet

install-nginx:	| $(ODROOT)/stages/added_deb_repos
	apt-get update
	apt-get install -y nginx

ifeq ($(DISTRO),debian)
$(ODROOT)/stages/added_deb_repos:	| $(ODROOT)/stages
	apt-get update
	apt-get install software-properties-common
	add-apt-repository contrib
	add-apt-repository non-free
	@touch $@
endif
ifeq ($(DISTRO),ubuntu)
$(ODROOT)/stages/added_deb_repos:	| $(ODROOT)/stages
	apt-get update
	apt-get install software-properties-common
	@touch $@
endif

$(ODROOT)/stages/dep_wkhtmltopdf:	| $(ODROOT)/stages $(ODROOT)/stages/system_user_created
	@wget -c https://github.com/wkhtmltopdf/packaging/releases/download/$(WKHTMLTOPDF_VERSION)/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb -O ~/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb
	@dpkg -i ~/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb || true
	@apt-get --fix-broken install -y
	@touch $@
