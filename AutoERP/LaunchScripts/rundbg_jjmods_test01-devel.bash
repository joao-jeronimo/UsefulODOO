export PYTHONPATH=/odoo/PythonLibs
sudo -u odoo /odoo/VirtualEnvs/Env_Python3.7_Odoo15.0/bin/python /odoo/releases/15.0/odoo-bin		\
	--database=jjmods_test01-devel --db-filter="jjmods_test01-devel.*"			\
	--config /odoo/configs/odoo-jjmods_test01-devel.conf					\
	--logfile /odoo/logs/odoo-jjmods_test01-devel.log
