
# ODOO 11:
export DBNAME="experiencia"
export DADIR="`pwd`"
cd ~/KTrabalho/GITs/ODOO11-git
source ~/KTrabalho/VirtualEnvs/odoove/bin/activate
./odoo-bin -d odoo11_"$DBNAME" --db-filter=odoo11_"$DBNAME.*" --db_user=jj --addons=addons/ --without-demo=all -p8011

# ODOO 12:
export DBNAME="experiencia"
export DADIR="`pwd`"
cd ~/KTrabalho/GITs/ODOO12-git
source ~/KTrabalho/VirtualEnvs/odoove/bin/activate
./odoo-bin -d odoo12_"$DBNAME" --db-filter=odoo12_"$DBNAME.*" --db_user=jj --addons=addons/ --without-demo=all -p8012

# ODOO 13:
export DBNAME="experiencia"
export DADIR="`pwd`"
cd ~/KTrabalho/GITs/ODOO13-git
source ~/KTrabalho/VirtualEnvs/odoove/bin/activate
pip3 install polib
./odoo-bin -d odoo13_"$DBNAME" --db-filter=odoo13_"$DBNAME.*" --db_user=jj --addons=addons/ --without-demo=all -p8013
