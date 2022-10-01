export INSTANCENM="jjmods-odoo14-elanceo-devel"
export PYTHONPATH=/odoo/PythonLibs
sudo -u odoo /odoo/VirtualEnvs/Env_Python3.7_Odoo14.0/bin/python /odoo/releases/14.0/odoo-bin		\
	--database="$INSTANCENM" --db-filter="$INSTANCENM.*"			\
	--config /odoo/configs/odoo-"$INSTANCENM".conf					\
	--logfile /odoo/logs/odoo-"$INSTANCENM".log
