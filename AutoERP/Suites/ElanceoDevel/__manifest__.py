{
    'name':         "Ajuda devel Elanceo - Odoo14",
    'odoo_branch':  "14.0",
    'repositories': [
        {
            'type':             "included",
            'srcpath':          "./Apps/Others/%(odoo_rel)s",
            'localname':        "Others",
            'odoo_releases':    ["14.0", ],
            'modpaths': [
                ".",
                ],
            },
        ],
    'modules':  [
        { 'name': 'hr_contract_types',              'active': True, },
        ],
}
