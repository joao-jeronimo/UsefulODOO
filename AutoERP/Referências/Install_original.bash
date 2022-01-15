#!/usr/bin/env bash

##############################################
###### Como adicionar novas instâncias: ######
##############################################
# Adicionar nova entrada ao case "labour_union_name".
# Criar um snapshot da VM.
# Executar este script como:
#    ./Install.bash nome_do_sindicato
# Depois executar o script de deploy manualmente.


#echo "Atenção: Rever código primeiro!"
#exit -1

# Correções a fazer:
# * Quando é devel, o que faz sentido é instalar na porta 8069 em vez da porta
#   certa do sindicato...
# * Quando é produção: copiar o repositório GIT.


if [ -z "$1" ]; then
echo "Sintaxe: $0 {sidildevel | sidiltestes | sidilrecycle | teste-sindicato | Refeitorio | UniLisboa | USL | STARQ | STAL | SIMAMEVIP}"
exit -1; fi

export labour_union_name=$1
export isdevel=$2

echo "A instalar para o sindicato $labour_union_name"
echo "Cancelar em 1 segundos primindo Ctrl-C..."
sleep 1

# This packages are necessary for the makefile to run:
sudo apt install -y make gmsl

# Fixed vars:
export ODOO_REL="13.0"
export INSTANCENM="`echo $labour_union_name | tr '[:upper:]' '[:lower:]'`"
export WKHTMLTOPDF_VERSION="0.12.6-1"
export DEBIAN_CODENAME="buster"
export INSTALLER_DIR="SIDIL-Installer"
export DEVEL_DIR="SIDIL-Odoo"
export INSTANCE_CODE_DIR="$labour_union_name"-SIDIL
# Always use main folder as runtime library path, so that bug as fixed everywhere:
export PYTHONLIBS_DIR=/odoo/sidilcode13/"$DEVEL_DIR"/PythonLibs
export PYTHON_VERSION="3.7"

if [ ! -d /odoo/sidilcode13/"$INSTALLER_DIR"/ ] ; then
    ###########################################################################
    ### This is when the user got the repository from somewhere else other  ###
    ### than /odoo/sidilcode13/SIDIL-Installer. In that case, the repo is   ###
    ### recloned on that diretory and the user is asked to rerun the script ###
    ### from there.                                                         ###
    ###########################################################################
    # Create top dirs for Odoo and SIDIL:
    sudo mkdir -p /odoo/
    sudo mkdir -p /odoo/sidilcode13/
    sudo mkdir -p /odoo/stages/
    # Create já the Odoo user and group - otherwise some operations will shortly fail:
    if [ ! -d /odoo/stages/system_user_created ] ; then
        sudo useradd -d /odoo/ odoo
        sudo touch /odoo/stages/system_user_created
    fi
    sudo usermod -aG odoo "$USER"
    #sudo chmod o+rwx /odoo/
    # Activate the environment:
    sudo -u "$USER" bash << EOF
source ../LaunchScripts/0_SetupEnvironment.bash --resetperms
# Clone the repo into the correct directory:
cd /odoo/sidilcode13/
git clone git@github.com:usl-cgtp-in/SIDIL-Odoo.git "$INSTALLER_DIR"
cd "$INSTALLER_DIR"
git checkout sidil_installer
EOF
    
    echo "# Por favor executar:"
    echo sudo -u "$USER" bash  # Para assumir o novo grupo, ou então fazer 'exit'.
    source /odoo/sidilcode13/"$INSTALLER_DIR"/External/LaunchScripts/0_SetupEnvironment.bash
    echo cd /odoo/sidilcode13/"$INSTALLER_DIR"/External/OdooBootstrap/
    echo $0 $@
    exit -1
fi

grep '### PRINT SIDIL CONTROL COMMANDS:' ~/.bashrc
if [ "$?" != 0 ] ; then
sudo -u "$USER" cat << EOF >> ~/.bashrc

### PRINT SIDIL CONTROL COMMANDS:
echo
echo "== Ativar ambiente do SIDIL:"
echo "source /odoo/sidilcode13/SIDIL-Installer/External/LaunchScripts/0_SetupEnvironment.bash"
echo "== Acesso às diretorias do SIDIL:"
echo "cd /odoo/sidilcode13/SIDIL-Installer/ ; git status"
echo "cd /odoo/sidilcode13/SIDIL-Odoo/ ; git status"
# Aliases for working with Odoo:
alias grepodoo='grep -Hnr --exclude="*.po" --exclude="*.pot" --exclude="*.pyc"'
alias odooports='grep http_port /odoo/configs/*'

EOF
fi

# Choose a HTTP port number:
case $labour_union_name in
  sidildevel)
    export INSTANCE_CODE_DIR="$DEVEL_DIR"
    export isdevel="--devel"
    export HTTPPORT=4080
    export INSTANCE_MODFOLDERS=/odoo/sidilcode13/"$DEVEL_DIR"
	export LISTEN_ON="0.0.0.0"
    export SCRIPT_NAME="./0_InstallSIDIL_empty.py"
    ;;
  sidiltestes)
    export INSTANCE_CODE_DIR="$DEVEL_DIR"
    export isdevel="--devel"
    export HTTPPORT=4083
    export INSTANCE_MODFOLDERS=/odoo/sidilcode13/"$DEVEL_DIR"
	export LISTEN_ON="0.0.0.0"
    export SCRIPT_NAME="./0_InstallSIDIL_empty.py"
    ;;
  sidilrecycle)
    export INSTANCE_CODE_DIR="$DEVEL_DIR"
    export isdevel="--devel"
    export HTTPPORT=4084
    export INSTANCE_MODFOLDERS=/odoo/sidilcode13/"$DEVEL_DIR"
	export LISTEN_ON="0.0.0.0"
    export SCRIPT_NAME="./0_InstallSIDIL_empty.py"
    ;;
  
  teste-sindicato)
    export INSTANCE_CODE_DIR="$DEVEL_DIR"
    export isdevel="--devel"
    export HTTPPORT=4087
    export INSTANCE_MODFOLDERS=/odoo/sidilcode13/"$DEVEL_DIR"
	export LISTEN_ON="0.0.0.0"
    export SCRIPT_NAME="./0_InstallSIDIL_Example_LabourUnionBase.py"
    ;;
	
  UniLisboa)
    export HTTPPORT=5000
    export INSTANCE_MODFOLDERS=/odoo/sidilcode13/"$DEVEL_DIR"
	export LISTEN_ON="127.0.0.1"
    export SCRIPT_NAME="./1_InstallSIDIL_$labour_union_name.py"
    ;;
  USL)
    export HTTPPORT=5001
    export INSTANCE_MODFOLDERS=/odoo/sidilcode13/"$INSTANCE_CODE_DIR"
	export LISTEN_ON="127.0.0.1"
    export SCRIPT_NAME="./1_InstallSIDIL_$labour_union_name.py"
    ;;
  STARQ)
    export HTTPPORT=5002
    export INSTANCE_MODFOLDERS=/odoo/sidilcode13/"$INSTANCE_CODE_DIR"
	export LISTEN_ON="127.0.0.1"
    export SCRIPT_NAME="./1_InstallSIDIL_$labour_union_name.py"
    ;;
  Refeitorio)
    export HTTPPORT=5003
    export INSTANCE_MODFOLDERS=/odoo/sidilcode13/"$INSTANCE_CODE_DIR"
	export LISTEN_ON="127.0.0.1"
    export SCRIPT_NAME="./1_InstallSIDIL_$labour_union_name.py"
    ;;
  STAL)
    export HTTPPORT=5004
    export INSTANCE_MODFOLDERS=/odoo/sidilcode13/"$INSTANCE_CODE_DIR"
	export LISTEN_ON="127.0.0.1"
    export SCRIPT_NAME="./1_InstallSIDIL_$labour_union_name.py"
    ;;
  SIMAMEVIP)
    export HTTPPORT=5005
    export INSTANCE_MODFOLDERS=/odoo/sidilcode13/"$INSTANCE_CODE_DIR"
	export LISTEN_ON="127.0.0.1"
    export SCRIPT_NAME="./1_InstallSIDIL_$labour_union_name.py"
    ;;
  *)
    echo "Sindicato desconhecido: $labour_union_name"
    ;;
esac

# Call makefile for virtualenv:
sudo --preserve-env=ODOO_REL,INSTANCENM,HTTPPORT,WKHTMLTOPDF_VERSION,DEBIAN_CODENAME,LISTEN_ON,INSTANCE_MODFOLDERS,PYTHON_VERSION,PYTHONLIBS_DIR make -f Odoo.makefile prepare_virtualenv
if [ "$?" != 0 ]
then
    echo "Falhou ao instalar a nova instância do Odoo."
    exit -1
fi

source /odoo/sidilcode13/"$INSTALLER_DIR"/External/LaunchScripts/0_SetupEnvironment.bash

sudo --preserve-env=ODOO_REL,INSTANCENM,HTTPPORT,WKHTMLTOPDF_VERSION,DEBIAN_CODENAME,LISTEN_ON,INSTANCE_MODFOLDERS,PYTHON_VERSION,PYTHONLIBS_DIR make -f Odoo.makefile prepare_all
if [ "$?" != 0 ]
then
    echo "Falhou ao instalar a nova instância do Odoo."
    exit -1
fi

source /odoo/sidilcode13/"$INSTALLER_DIR"/External/LaunchScripts/0_SetupEnvironment.bash --resetperms

# Copy the development tree to a specific dir of the trade union being deployed. This is always done, even if we are 
cd "/odoo/sidilcode13/"
if [ ! -d ./"$DEVEL_DIR"/ ] ; then
    sudo -u odoo cp -av "$INSTALLER_DIR" "$DEVEL_DIR"
    cd "$DEVEL_DIR"
    git checkout main
    git pull --all
fi
if [ ! -d ./"$INSTANCE_CODE_DIR"/ ] ; then
    sudo -u odoo cp -av "$DEVEL_DIR" "$INSTANCE_CODE_DIR"
fi

# The command that the user must enter in order to go to the correct directory:
export CHDIR_COMMAND="cd '/odoo/sidilcode13/$INSTALLER_DIR/External/NewDeploy'"

echo '#####################################'
echo 'Now call deploy script:'
echo "sudo systemctl start odoo-$INSTANCENM"
echo "tail -f /odoo/logs/odoo-$INSTANCENM.log"
echo "$CHDIR_COMMAND"
echo "$SCRIPT_NAME"
echo "# To delete the database, do: sudo -u postgres dropdb $INSTANCENM"
