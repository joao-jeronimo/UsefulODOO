############################
### Vars:
ODOO_REL=13.0
INSTANCENM=base13
HTTPPORT=4013

WKHTMLTOPDF_VERSION=0.12.6-1

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


$(SYSTEMD_PATH)/odoo-$(INSTANCENM).service:  | $(ODROOT)/configs/odoo-$(INSTANCENM).conf
	@echo "Installing SystemD config file $@..."
	@sed "s/INSTANCENM/$(INSTANCENM)/g;s/ODOO_USERNAME/$(ODOO_USERNAME)/g;s/ODOO_REL/$(ODOO_REL)/g;s/ODROOT/$(ODROOT:/%=\\/%)/g" template.service > $@

$(ODROOT)/configs/odoo-$(INSTANCENM).conf:  | $(ODROOT)/releases/$(ODOO_REL) $(ODROOT)/configs
	@echo "Installing config file $@..."
	@sed "s/INSTANCENM/$(INSTANCENM)/g;s/ODOO_USERNAME/$(ODOO_USERNAME)/g;s/ODOO_REL/$(ODOO_REL)/g;s/ODROOT/$(ODROOT:/%=\\/%)/g;s/HTTPPORT/$(HTTPPORT)/g" template.conf > $@

$(ODROOT)/releases/$(ODOO_REL): | $(ODROOT)/odoo-full-git $(ODROOT)/releases
	@echo "Checking out $(ODOO_REL) branch..."
	@cd $(ODROOT)/odoo-full-git ; git checkout $(ODOO_REL)
	@cd $(ODROOT)/odoo-full-git ; git pull --all
	@echo "Fetching $(ODOO_REL) branch..."
	@git clone -b $(ODOO_REL) --single-branch $(ODROOT)/odoo-full-git $@

$(ODROOT)/odoo-full-git:   | $(ODROOT)
	@echo "Fetching Odoo source from git"
	@git clone "$(MAIN_GIT_REMOTE_REPO)" $@

$(ODROOT):
	mkdir $@
$(ODROOT)/releases $(ODROOT)/configs $(ODROOT)/logs:  | $(ODROOT)
	mkdir $@
