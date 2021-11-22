###############################################
### Dependencies to run this on Debian/Ubuntu:
# sudo apt install make git screenie
### To invoke:
# sudo make -f Makefile.mak

############################
### Vars:
ifeq ($(ODOO_REL),)
ODOO_REL=15.0
endif
ifeq ($(INSTANCENM),)
INSTANCENM=base15
endif
ifeq ($(HTTPPORT),)
HTTPPORT=4015
endif
ifeq ($(WKHTMLTOPDF_VERSION),)
WKHTMLTOPDF_VERSION=0.12.6-1
endif
ifeq ($(DEBIAN_CODENAME),)
DEBIAN_CODENAME=focal
endif

############################
### Constants:
ODROOT=/odoo
MAIN_GIT_REMOTE_REPO=https://github.com/odoo/odoo.git
ODOO_USERNAME=odoo
SYSTEMD_PATH=/lib/systemd/system

############################
.PHONY: default_target prepare_$(INSTANCENM)
default_target:	prepare_$(INSTANCENM)

prepare_$(INSTANCENM):  $(SYSTEMD_PATH)/odoo-$(INSTANCENM).service


$(SYSTEMD_PATH)/odoo-$(INSTANCENM).service:  | $(ODROOT)/configs/odoo-$(INSTANCENM).conf $(ODROOT)/stages/dep_branch_requirements $(ODROOT)/stages/dep_wkhtmltopdf $(ODROOT)/stages/system_user_created
	@echo "Installing SystemD config file $@..."
	@sed "s/INSTANCENM/$(INSTANCENM)/g;s/ODOO_USERNAME/$(ODOO_USERNAME)/g;s/ODOO_REL/$(ODOO_REL)/g;s/ODROOT/$(ODROOT:/%=\\/%)/g" template.service > $@
	@chown odoo:odoo -Rc /odoo/
	@chmod ug+rwX -Rc /odoo/
	@chmod o-rwx -Rc /odoo/
	@find /odoo/ -type d -exec chmod g+s {} \;

$(ODROOT)/configs/odoo-$(INSTANCENM).conf:  | $(ODROOT)/releases/$(ODOO_REL) $(ODROOT)/configs $(ODROOT)/custom_$(ODOO_REL) $(ODROOT)/stages/sql_user_created
	@echo "Installing config file $@..."
	@sed "s/INSTANCENM/$(INSTANCENM)/g;s/ODOO_USERNAME/$(ODOO_USERNAME)/g;s/ODOO_REL/$(ODOO_REL)/g;s/ODROOT/$(ODROOT:/%=\\/%)/g;s/HTTPPORT/$(HTTPPORT)/g" template.conf > $@

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
	mkdir $@
$(ODROOT)/releases $(ODROOT)/configs $(ODROOT)/logs $(ODROOT)/custom_$(ODOO_REL) $(ODROOT)/stages:  | $(ODROOT)
	mkdir $@

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
	@touch $@
$(ODROOT)/stages/dep_pip_packages:	| $(ODROOT)/stages $(ODROOT)/stages/dep_apt_packages
	sudo -H pip3 install --upgrade pip
	sudo -H pip3 install --upgrade six pillow python-dateutil pytz unidecode
	sudo -H pip3 install --ignore-installed pyserial psycopg2-binary
	@touch $@
$(ODROOT)/stages/dep_apt_packages:	| $(ODROOT)/stages
	apt-get update
	apt-get install -y python3-pip
	apt-get install -y postgresql postgresql-client
	apt-get install -y ttf-mscorefonts-installer node-less
	apt-get install -y libpq-dev libjpeg-dev libxml2-dev libxslt-dev zlib1g-dev
	apt-get build-dep -y python3-ldap
	@touch $@
$(ODROOT)/stages/dep_wkhtmltopdf:	| $(ODROOT)/stages
	@wget -c https://github.com/wkhtmltopdf/packaging/releases/download/$(WKHTMLTOPDF_VERSION)/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb -O ~/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb
	@dpkg -i ~/wkhtmltox_$(WKHTMLTOPDF_VERSION).$(DEBIAN_CODENAME)_amd64.deb || true
	@apt-get --fix-broken install -y
	@touch $@

.PHONY: listports
listports:
	grep -Hnr http_port /odoo/configs/
	grep -Hnr http_port /odoo/configs/ | grep -o [0-9][0-9][0-9][0-9] | sort
