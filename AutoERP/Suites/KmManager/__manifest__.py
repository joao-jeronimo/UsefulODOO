{
    'name':         "Km expense calculator - Odoo14",
    'repositories': [
        {
            'type':             "included",
            'srcpath':          "./Apps/Payroll/%(odoo_rel)s",
            'localname':        "Payroll",
            'odoo_releases':    [ "14.0", ],
            'modpaths': [
                ".",
                ],
            },
        {
            'type':             "included",
            'srcpath':          "./Devel/",
            'localname':        "ExpenseMilleage",
            'odoo_releases':    [ "14.0", ],
            'modpaths': [
                ".",
                ],
            },
        ],
    'modules':  [
        { 'name': 'hr_contract_types',              'active': True, },
        { 'name': 'hr_payroll_community',           'active': True, },
        
        { 'name': 'hr_expense',                     'active': True, },
        #{ 'name': 'hr_expense_milleage_allowances', 'active': True, },
        ],
}
