############################
### Vars:
ODOO_REL="13.0"
INSTANCENM="base13"

WKHTMLTOPDF_VERSION="0.12.6-1"

############################
### Constants:
ODROOT="/odoo"
MAIN_GIT_REMOTE_REPO="https://github.com/odoo/odoo.git"
ODOO_USERNAME="odoo"
SYSTEMD_PATH=/etc/systemd/system/multi-user.target.wants

############################
default_target:	prepare_$(INSTANCENM)
	


prepare_$(INSTANCENM):  $(SYSTEMD_PATH)/odoo-$(INSTANCENM).service


$(SYSTEMD_PATH)/odoo-$(INSTANCENM).service:  $(ODROOT)/configs/odoo-$(INSTANCENM).conf
    

$(ODROOT)/configs/odoo-$(INSTANCENM).conf:  $(ODROOT)/releases/$(ODOO_REL)



$(ODROOT)/releases/$(ODOO_REL): $(ODROOT)/odoo-full-git
	@echo "Fetching $(ODOO_REL) branch..."
	@git clone -b $(ODOO_REL) --single-branch $(ODROOT)/odoo-full-git $@

$(ODROOT)/odoo-full-git:   $(ODROOT)
	@echo "Fetching Odoo source from git"
	@git clone "$(MAIN_GIT_REMOTE_REPO)" $@

$(ODROOT):
	mkdir $@
$(ODROOT)/releases $(ODROOT)/configs $(ODROOT)/logs:  $(ODROOT)
	mkdir $@
