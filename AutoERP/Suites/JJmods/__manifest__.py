{
    'name':         "JJ Modules for payroll and so",
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
            'odoo_releases':    ["11.0", "12.0", "13.0", "14.0", "15.0", ],
            # Python function to port the modules after clone/checkout.
            'post_fetch_hook':  "port_modules_odoo",
            'modpaths': [
                "0_Installable/%(odoo_rel)s",
                ],
            },
        ],
    'modules':  [
        # Base apps:
        { 'name': 'hr_payroll',                     'active': ["11.0", "12.0",                         ], },
        { 'name': 'hr_payroll_community',           'active': [                "13.0", "14.0", "15.0", ], },
        { 'name': 'hr_contract_types',              'active': [                "13.0", "14.0", "15.0", ], },
        # Generic features:
        { 'name': 'payslip_aggregate_rule',         'active': True, },
        { 'name': 'payroll_typesafe_formulas',      'active': True, },
        { 'name': 'payslip_effective_dates',        'active': True, },
        { 'name': 'payslip_advanced_info_tab',      'active': True, },
        { 'name': 'payslip_proportional_bases',     'active': True, },
        # PDF templates:
        { 'name': 'alternative_detailed_payslip',   'active': True, },
        { 'name': 'alternative_french_payslip',     'active': True, },
        { 'name': 'simple_payslip_template',        'active': True, },
        # Demo data and tests:
        { 'name': 'hr_payroll_community_demo_data', 'active': True, },
        ],
}
