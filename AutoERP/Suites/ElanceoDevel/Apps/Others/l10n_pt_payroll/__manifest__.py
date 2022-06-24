#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Localização da Folha salarial para Portugal (Payroll localization for Portugal)',
    'category': 'Human Resources',
    'sequence': 906,
    'summary': 'Payroll localization for Portugal',
    'description': "Payroll localization for Portugal. This new version is comptible with Odoo Community Payroll modules.",
    'author': 'João Jerónimo',
    
    'application': False,
    'installable': True,
    
    'version': "14.1.90",
    'license': 'LGPL-3',
    
    'depends': [
        'hr_payroll_community',
        'payslip_aggregate_rule',
    ],
    'data': [
        'categories.xml',
        
        #'rules/basic.xml',
        #'rules/tsu.xml',
        #'rules/irs.xml',
        #'rules/subsidioss.xml',
        
        #'structs.xml',
    ],
#    'demo': [  ],
}
