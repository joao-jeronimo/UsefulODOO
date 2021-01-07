############################
### Vars:
ODOO_REL="13.0"
INSTANCENM="base13"
HTTPPORT=4013

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
	@echo "Installing SystemD config file $@..."
	@cat << EOF > "$@"
	[Unit]
	Description=Odoo-instance-$(INSTANCENM)
	After=network.target
	
	[Service]
	Type=simple
	User=$(ODOO_USERNAME)
	Group=$(ODOO_USERNAME)
	ExecStart=$(ODROOT)/releases/$(ODOO_REL)/odoo-bin --database=$(INSTANCENM) --db-filter="$(INSTANCENM).*" --config /odoo/configs/odoo-$(INSTANCENM).conf --logfile /odoo/logs/odoo-$(INSTANCENM).log
	KillMode=mixed
	
	[Install]
	WantedBy=multi-user.target
	EOF

$(ODROOT)/configs/odoo-$(INSTANCENM).conf:  $(ODROOT)/releases/$(ODOO_REL)
	@echo "Installing config file $@..."
	@cat << EOF > "$@"
	[options]
	addons_path = $(ODROOT)/releases/$(ODOO_REL)/addons
	#admin_passwd =
	csv_internal_sep = ,
	data_dir = /odoo/.local/share/Odoo
	#db_host = localhost
	#db_port = 5432
	#db_password = (not needed)
	db_maxconn = 64
	db_name = $(INSTANCENM)
	db_sslmode = prefer
	db_template = template1
	db_user = $(ODOO_USERNAME)
	demo = {}
	email_from = False
	;geoip_database = /usr/share/GeoIP/GeoLite2-City.mmdb
	http_enable = True
	http_interface = 0.0.0.0
	http_port = $(HTTPPORT)
	import_partial = 
	limit_memory_hard = 2684354560
	limit_memory_soft = 2147483648
	limit_request = 8192
	limit_time_cpu = 60
	limit_time_real = 120
	limit_time_real_cron = -1
	list_db = True
	log_db = False
	log_db_level = warning
	log_handler = :INFO
	log_level = info
	logrotate = False
	longpolling_port = 8072
	max_cron_threads = 2
	osv_memory_age_limit = 1.0
	osv_memory_count_limit = False
	pg_path = None
	pidfile = False
	proxy_mode = True
	reportgz = False
	server_wide_modules = web
	smtp_password = False
	smtp_port = 25
	smtp_server = localhost
	smtp_ssl = False
	smtp_user = False
	syslog = False
	test_commit = False
	test_enable = False
	test_file = False
	test_report_directory = False
	translate_modules = ['all']
	unaccent = False
	without_demo = True
	workers = 0
	EOF

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
