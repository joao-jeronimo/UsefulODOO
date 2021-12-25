###############################################
### Dependencies to run this on Debian/Ubuntu:
# sudo apt install make git screenie
### To invoke:
# sudo make -f Makefile.mak

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
ifeq ($(DEBIAN_CODENAME),)
$(error Var DEBIAN_CODENAME not defined.)
endif
ifeq ($(PYTHONLIBS_DIR),)
$(error Var PYTHONLIBS_DIR not defined.)
endif

# Vars with defaults:
ifeq ($(LISTEN_ON),)
LISTEN_ON=127.0.0.1
endif

# Non-mandatory variables:
#ifeq ($(INSTANCE_MODFOLDERS),)
#$(error Var INSTANCE_MODFOLDERS not defined.)
#endif

# Example var assignments for bash:
#export ODOO_REL=13.0
#export INSTANCENM=base13
#export HTTPPORT=4083
#export WKHTMLTOPDF_VERSION=0.12.6-1
#export DEBIAN_CODENAME=buster

############################
### Constants:
ODROOT=/odoo
MAIN_GIT_REMOTE_REPO=https://github.com/odoo/odoo.git
ODOO_USERNAME=odoo
SYSTEMD_PATH=/lib/systemd/system
############################
### Sedable versions of args:
SEDABLE_ODROOT:=$(subst /,\/,$(ODROOT))
SEDABLE_INSTANCE_MODFOLDERS:=$(subst /,\/,$(INSTANCE_MODFOLDERS))
SEDABLE_PYTHONLIBS_DIR:=$(subst /,\/,$(PYTHONLIBS_DIR))

############################
.PHONY: default_target prepare_$(INSTANCENM)
default_target:	prepare_$(INSTANCENM)

prepare_$(INSTANCENM):  $(SYSTEMD_PATH)/odoo-$(INSTANCENM).service


$(SYSTEMD_PATH)/odoo-$(INSTANCENM).service:  | $(ODROOT)/configs/odoo-$(INSTANCENM).conf $(ODROOT)/stages/dep_branch_requirements $(ODROOT)/stages/dep_wkhtmltopdf $(ODROOT)/stages/system_user_created $(ODROOT)/logs
	@echo "Installing SystemD config file $@..."
	@sed 's/INSTANCENM/$(INSTANCENM)/g;s/ODOO_USERNAME/$(ODOO_USERNAME)/g;s/ODOO_REL/$(ODOO_REL)/g;s/ODROOT/$(SEDABLE_ODROOT)/g;s/PYTHONLIBS_DIR/$(SEDABLE_PYTHONLIBS_DIR)/g' template.service > "$@"
	# Everything same user:
	@chown "$(ODOO_USERNAME):$(ODOO_USERNAME)" -Rc /odoo/
	@bash -c "chmod ug+rwX -R /odoo/{configs,logs,stages}"
	@bash -c "chmod u+rwX,g+rX,g-w -R /odoo/{odoo-full-git,releases}"
	@chmod o-wx,o+rX -R /odoo/
	@find /odoo/ -type d -exec chmod g+s {} \;

$(ODROOT)/configs/odoo-$(INSTANCENM).conf:  | $(ODROOT)/releases/$(ODOO_REL) $(ODROOT)/configs $(ODROOT)/stages/sql_user_created
	@echo "Installing config file $@..."
	@sed 's/INSTANCENM/$(INSTANCENM)/g;s/ODOO_USERNAME/$(ODOO_USERNAME)/g;s/LISTEN_ON/$(LISTEN_ON)/g;s/ODOO_REL/$(ODOO_REL)/g;s/ODROOT/$(SEDABLE_ODROOT)/g;s/HTTPPORT/$(HTTPPORT)/g;s/INSTANCE_MODFOLDERS/$(SEDABLE_INSTANCE_MODFOLDERS)/g' template.conf > "$@"

$(ODROOT)/releases/$(ODOO_REL): | $(ODROOT)/odoo-full-git $(ODROOT)/releases
	@echo "Checking out $(ODOO_REL) branch..."
	@cd $(ODROOT)/odoo-full-git ; git checkout $(ODOO_REL)
	@cd $(ODROOT)/odoo-full-git ; git pull --all
	@echo "Fetching $(ODOO_REL) branch..."
	@git clone -b $(ODOO_REL) --single-branch $(ODROOT)/odoo-full-git $@

$(ODROOT)/odoo-full-git:   | $(ODROOT) $(ODROOT)/stages/dep_git_deb
	@echo "Fetching Odoo source from git"
	@git clone "$(MAIN_GIT_REMOTE_REPO)" $@

$(ODROOT):
	mkdir -p $@
$(ODROOT)/releases $(ODROOT)/configs $(ODROOT)/logs $(ODROOT)/stages $(ODROOT)/python-packages:  | $(ODROOT)
	mkdir -p $@

# Permissions config:
$(ODROOT)/stages/sql_user_created:	| $(ODROOT)/stages $(ODROOT)/stages/dep_apt_packages
	sudo -u postgres bash -c "createuser -s $(ODOO_USERNAME)"
	@touch $@
$(ODROOT)/stages/system_user_created:	| $(ODROOT)/stages
	useradd -d $(ODROOT) $(ODOO_USERNAME)
	@touch $@

# Dependencies installation:
$(ODROOT)/stages/dep_git_deb:	| $(ODROOT)/stages
	sudo apt-get install git
	@touch $@
$(ODROOT)/stages/dep_branch_requirements:	| $(ODROOT)/stages $(ODROOT)/stages/dep_apt_packages $(ODROOT)/stages/dep_pip_packages
	cd $(ODROOT)/releases/$(ODOO_REL) ; sudo -H pip3 install -r requirements.txt
	sudo -H pip3 install --upgrade num2words
	# Dependencies for the deploy scripts:
	sudo -H pip3 install pymssql odoo-import-export-client odoo-client-lib ezodf gitpython
	@touch $@
$(ODROOT)/stages/dep_pip_packages:	| $(ODROOT)/stages $(ODROOT)/stages/dep_apt_packages
	sudo -H pip3 install --upgrade pip
	sudo -H pip3 install --upgrade six pillow python-dateutil pytz unidecode xlutils
	sudo -H pip3 install --ignore-installed pyserial
	# Force install PortgreSQL API (psycopg2) from source:
	sudo -H pip3 install --ignore-installed --no-binary :all: psycopg2
	@touch $@
$(ODROOT)/stages/dep_apt_packages:	| $(ODROOT)/stages
	apt-get update
	apt-get install software-properties-common
	add-apt-repository contrib
	add-apt-repository non-free
	apt-get update
	apt-get install -y python3-pip
	apt-get install -y postgresql postgresql-client
	apt-get install -y ttf-mscorefonts-installer fonts-lato node-less
	apt-get install -y libpq-dev libjpeg-dev libxml2-dev libxslt-dev zlib1g-dev
	apt-get build-dep -y python3-ldap
	@touch $@
$(ODROOT)/stages/dep_wkhtmltopdf:	| $(ODROOT)/stages $(ODROOT)/stages/system_user_created
	@wget -c https://github.com/wkhtmltopdf/packaging/releases/download/$(WKHTMLTOPDF_VERSION)/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb -O ~/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb
	@dpkg -i ~/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb || true
	@apt-get --fix-broken install -y
	@touch $@
