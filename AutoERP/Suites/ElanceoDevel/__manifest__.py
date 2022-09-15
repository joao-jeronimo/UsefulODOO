{
    'name':         "Ajuda devel Elanceo - Odoo14",
    'repositories': [
        {
            'type':             "included",
            'srcpath':          "./IncludedApps/%(odoo_rel)s",
            'localname':        "Others",
            'odoo_releases':    ["14.0", ],
            'modpaths': [
                ".",
                ],
            },
        ],
    'modules':  [
        #{ 'name': 'hr_contract_types',              'active': False, },
        ],
}
