{
    'name': 'Rich Payslip Editing - A fork of payslip_review module',
    'description'   : 'A fork of https://apps.odoo.com/apps/modules/12.0/payslip_review/'
    'version': '14.0.01',
    'author': 'João Jerónimo',
    'category': 'Payroll',
    'data': [
        'views/hr_payslip_views.xml',
    ],
    'depends' : [
        'base',
        'web',
        'hr_payroll_community'
        ],
    'qweb': [
        'static/src/xml/*.xml',
        ],
    'installable': True,
}

