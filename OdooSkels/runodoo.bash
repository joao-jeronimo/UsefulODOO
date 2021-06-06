# Preparação do sistema:
sudo apt install sassc
pip3 install polib


# ODOO 11:
export DBNAME="test"
export DADIR="`pwd`"
cd ~/KTrabalho/GITs/Odoo11-git
source ~/KTrabalho/VirtualEnvs/odoove/bin/activate
./odoo-bin -d odoo11_"$DBNAME" --db-filter=odoo11_"$DBNAME.*" --db_user=jj --addons=addons/ --without-demo=all -p8011

# ODOO 12:
export DBNAME="test"
export DADIR="`pwd`"
cd ~/KTrabalho/GITs/Odoo12-git
source ~/KTrabalho/VirtualEnvs/odoove/bin/activate
./odoo-bin -d odoo12_"$DBNAME" --db-filter=odoo12_"$DBNAME.*" --db_user=jj --addons=addons/ --without-demo=all -p8012

# ODOO 13:
export DBNAME="test"
export DADIR="`pwd`"
cd ~/KTrabalho/GITs/Odoo13-git
source ~/KTrabalho/VirtualEnvs/odoove/bin/activate
./odoo-bin -d odoo13_"$DBNAME" --db-filter=odoo13_"$DBNAME.*" --db_user=jj --addons=addons/ --without-demo=all -p8013
