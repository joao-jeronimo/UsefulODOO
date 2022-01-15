export ISINIT=$1
case $ISINIT in
  "--resetperms")
    
    sudo chown odoo:odoo -Rc /odoo/
    sudo find /odoo/ -type d -exec chmod g+s {} \;
    sudo bash -c "chmod ug+rwX /odoo/"
    
    sudo bash -c "chmod ug+rwX -R /odoo/{odoo-full-git,releases}"
    sudo bash -c "chmod ug+rwX -R /odoo/AutoERP/"
    sudo bash -c "chmod ug+rwX -R /odoo/VirtualEnvs/"
    
    sudo bash -c "chmod u+rwX,g+rX,g-w -R /odoo/{configs,logs,stages}"
    
    sudo chmod o-wx,o+rX -R /odoo/
    
    ;;
esac

umask 0002

source /odoo/VirtualEnvs/Env_Python3.7_Odoo13.0/bin/activate
