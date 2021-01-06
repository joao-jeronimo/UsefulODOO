############################
### Vars:
export ODOOMAN_DIR="/odoo"
export ODOOMAN_ODOO_REL="13.0"

export MAIN_GIT_REMOTE_REPO="https://github.com/odoo/odoo.git"
export MAIN_GIT_LOCAL_REPO="$(ODOOMAN_DIR)"/odoo-full-git
export SCRIPTCONFIG="$(ODOOMAN_DIR)"/odooconfig.conf
export RELEASES_DIR="$(ODOOMAN_DIR)"/releases
export ODOO_USERNAME="odoo"

export WKHTMLTOPDF_VERSION="0.12.6-1"

############################
default_target:	$(MAIN_GIT_LOCAL_REPO)
	



$(MAIN_GIT_LOCAL_REPO):
	@echo "Fetching Odoo source from git"
	@git clone "$(MAIN_GIT_REMOTE_REPO)" "$(MAIN_GIT_LOCAL_REPO)"
