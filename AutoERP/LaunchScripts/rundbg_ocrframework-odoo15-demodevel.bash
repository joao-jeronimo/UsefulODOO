sudo systemctl stop odoo-ocrframework-odoo15-demodevel
export PYTHONPATH=/odoo/PythonLibs
sudo -u odoo /odoo/VirtualEnvs/Env_Python3.7_Odoo15.0/bin/python /odoo/releases/15.0/odoo-bin		\
	--database="ocrframework-odoo15-demodevel" --db-filter="ocrframework-odoo15-demodevel.*"			\
	--config /odoo/configs/odoo-ocrframework-odoo15-demodevel.conf					\
	--logfile /odoo/logs/odoo-ocrframework-odoo15-demodevel.log
