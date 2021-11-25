#!/usr/bin/env bash

##############################################
###### Como adicionar novas instâncias: ######
##############################################
# Adicionar nova entrada ao case "instance_preset_name".
# Criar um snapshot da VM.
# Executar este script como:
#    ./Install.bash nome_da_base
# Depois executar o script de deploy manualmente.

#echo "Atenção: Rever código primeiro!"
#exit -1

if [ -z "$1" ]; then
echo "Sintaxe: $0 { base11 | base12 | base13 | base14 | base15 }"
exit -1; fi

export instance_preset_name=$1
export isdevel=$2

echo "A instalar para a base $instance_preset_name"
echo "Cancelar em 1 segundos primindo Ctrl-C..."
sleep 1

# This packages are necessary for the makefile to run:
sudo apt install -y make gmsl

# Fixed vars:
export INSTANCENM="`echo $instance_preset_name | tr '[:upper:]' '[:lower:]'`"
export WKHTMLTOPDF_VERSION="0.12.6-1"
export DEBIAN_CODENAME="buster"
export CUSTOM_MODS_DIR="custom_$ODOO_REL"

mkdir -p "$CUSTOM_MODS_DIR/other_mods"

# Choose a HTTP port number:
case $instance_preset_name in
  base11)
    export ODOO_REL="11.0"
    export HTTPPORT=4011
    export INSTANCE_MODFOLDERS="/odoo/$CUSTOM_MODS_DIR/other_mods"
    export PYTHONLIBS_DIR=/odoo/PythonLibs
	# The commands that the user has to run after bootstrapping Odoo:
    export CHDIR_COMMAND="cd '/odoo/$CUSTOM_MODS_DIR'"
    export SCRIPT_NAME=""
    ;;
  base12)
    export ODOO_REL="12.0"
    export HTTPPORT=4012
    export INSTANCE_MODFOLDERS=""
    export PYTHONLIBS_DIR=/odoo/PythonLibs
	# The commands that the user has to run after bootstrapping Odoo:
    export CHDIR_COMMAND="cd '/odoo/$CUSTOM_MODS_DIR'"
    export SCRIPT_NAME=""
    ;;
  base13)
    export ODOO_REL="13.0"
    export HTTPPORT=4013
    export INSTANCE_MODFOLDERS=""
    export PYTHONLIBS_DIR=/odoo/PythonLibs
	# The commands that the user has to run after bootstrapping Odoo:
    export CHDIR_COMMAND="cd '/odoo/$CUSTOM_MODS_DIR'"
    export SCRIPT_NAME=""
    ;;
  base14)
    export ODOO_REL="14.0"
    export HTTPPORT=4014
    export INSTANCE_MODFOLDERS=""
    export PYTHONLIBS_DIR=/odoo/PythonLibs
	# The commands that the user has to run after bootstrapping Odoo:
    export CHDIR_COMMAND="cd '/odoo/$CUSTOM_MODS_DIR'"
    export SCRIPT_NAME=""
    ;;
  base15)
    export ODOO_REL="15.0"
    export HTTPPORT=4015
    export INSTANCE_MODFOLDERS=""
    export PYTHONLIBS_DIR=/odoo/PythonLibs
	# The commands that the user has to run after bootstrapping Odoo:
    export CHDIR_COMMAND="cd '/odoo/$CUSTOM_MODS_DIR'"
    export SCRIPT_NAME=""
    ;;
    
  *)
    echo "Base desconhecida: $instance_preset_name"
    ;;
esac

# Conditional vars common to every target:
if [ "$isdevel" = "--devel" ]
then
    export LISTEN_ON="0.0.0.0"
fi

# Call makefile:
sudo --preserve-env=ODOO_REL,INSTANCENM,HTTPPORT,WKHTMLTOPDF_VERSION,DEBIAN_CODENAME,LISTEN_ON,INSTANCE_MODFOLDERS,PYTHONLIBS_DIR make -f Odoo.makefile
if [ "$?" != 0 ]
then
    echo "Falhou ao instalar a nova instância do Odoo."
    exit -1
fi

echo '### Install done! #####################################'
echo "sudo systemctl start odoo-$INSTANCENM"
echo "tail -f /odoo/logs/odoo-$INSTANCENM.log"
echo "$CHDIR_COMMAND"
echo "# To delete the database, run: sudo -u postgres dropdb $INSTANCENM"
