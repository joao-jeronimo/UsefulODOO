cd ../ODOO11-git
source ../odoove/bin/activate
./odoo-bin -d sobase --db-filter=sobase --db_user=jj --addons=addons/,../UsefulODOO/themes/enterprise_theme/ --without-demo=all
