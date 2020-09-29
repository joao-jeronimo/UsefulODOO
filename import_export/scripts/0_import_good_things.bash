#sudo apt install python3-pip
#sudo -H pip3 install --ungrade pip
#sudo -H pip3 install odoo-import-export-client

# Se necessário, desativar a validação TLS em:
# /usr/local/lib/python3.6/dist-packages/odoolib/main.py; Linha 116; acrescentar argumento ", verify=False"


echo "Rever script primeiro!"
exit


export_named_thing () {
    export outfile=$1
    export model=$2
    export fields=$3
    shift 3
    odoo_export_thread.py -c scripts/src_connection.conf --model "$model" --file "$outfile" --field "id,$fields" --context="{'active_test':False}" --worker=3 --size=100 $* 2>> all_export_errors.log
}
import_named_thing () {
    export infile=$1
    export model=$2
    shift 2
    odoo_import_thread.py -s ";" -c scripts/dst_connection.conf --model "$model" --file "$infile" --size 100 $* 2>> all_import_errors.log
}

export_thing () {
    export_named_thing $1.csv $*
}
import_thing () {
    import_named_thing $1.csv $*
}

migrate_m2o_field () {
    export model=$1
    export fieldname=$2
    export filtdomain=$3
    shift 2
    shift 1
    export_named_thing "$model"_"$fieldname".csv "$model" "$fieldname"/id --domain "[(\"$fieldname\",'!=',False)$filtdomain]"
    import_named_thing "$model"_"$fieldname".csv "$model" --size=150 --groupby "$fieldname"/id $*
}

rm -f all_import_errors.log

############# HR data:
import_thing "resource.calendar.leaves"
import_thing "hr.job"
import_thing "hr.employee.category"
import_thing "hr.employee"
import_thing "hr.department"
import_thing "hr.contract"
import_named_thing "hr.contract_overrides.csv" "hr.contract"

############# Payslips:
import_thing "hr.payslip.run"
import_thing "hr.payslip"  --context "{'check_net_existence':False}"
import_thing "hr.payslip.line"
import_thing "hr.payslip.input"


sed -i "s/\\\n/\n/g" all_import_errors.log
