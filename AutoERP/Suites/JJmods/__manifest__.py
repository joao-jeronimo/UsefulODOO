{
    'name':         "JJ Modules for payroll and so - Odoo15",
    'odoo_branch':  "15.0",
    'repositories': [
        {
            'type':             "included",
            'srcpath':          "./Apps/Payroll/%(odoo_rel)s",
            'localname':        "Payroll",
            'odoo_releases':    ["13.0", "14.0", "15.0", ],
            'modpaths': [
                ".",
                ],
            },
        {
            'type':             "git",
            'url':              "git@github.com:joao-jeronimo/SimplePayslipTemplate.git",
            'localname':        "SimplePayslipTemplate",
            'branch':           "apps-dev",
            # Python function to port the modules after clone/checkout.
            'post_fetch_hook':  "port_modules_odoo",
            'modpaths': [
                "0_Installable/%(odoo_rel)s",
                ],
            },
        ],
    'modules':  [
        { 'name': 'hr_contract_types',              'active': True, },
        { 'name': 'hr_payroll_community',           'active': True, },
        
        { 'name': 'alternative_detailed_payslip',   'active': True, },
        { 'name': 'payslip_aggregate_rule',         'active': True, },
        { 'name': 'payroll_typesafe_formulas',      'active': True, },
        { 'name': 'payslip_effective_dates',        'active': True, },
        { 'name': 'payslip_advanced_info_tab',      'active': True, },
        { 'name': 'payslip_proportional_bases',     'active': True, },
        ],
}
