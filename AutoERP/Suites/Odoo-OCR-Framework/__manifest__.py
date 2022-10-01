{
    'name':         "A set of OCR wrappers for Odoo",
    'repositories': [
        #{
        #    'type':             "included",
        #    'srcpath':          "./Apps/Payroll/%(odoo_rel)s",
        #    'localname':        "Payroll",
        #    'odoo_releases':    ["13.0", "14.0", "15.0", ],
        #    'modpaths': [
        #        ".",
        #        ],
        #    },
        {
            'type':             "git",
            'url':              "git@github.com:joao-jeronimo/Odoo-OCR.git",
            'localname':        "Odoo-OCR",
            'branch':           "main",
            'odoo_releases':    [
                #"11.0",
                #"12.0",
                #"13.0",
                #"14.0",
                "15.0",
                ],
            # Python function to port the modules after clone/checkout.
            'post_fetch_hook':  "port_modules_odoo",
            'modpaths': [
                "0_Installable/%(odoo_rel)s",
                ],
            },
        ],
    'modules':  [
        # Base apps:
        #{ 'name': 'tesseract_wrapper',                  'active': ["15.0", ], },
        ],
}
