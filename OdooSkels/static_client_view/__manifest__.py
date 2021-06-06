{
    'name': 'A static client view skel module',
    'version': '14.0.01',
    'author': 'João Jerónimo',
    'category': 'Payroll',
    'data': [
        'views_and_actions.xml',
    ],
    'depends' : [
        'hr_payroll_community'
        ],
    'qweb': [
        'static/src/xml/*.xml',
        ],
    'installable': True,
}

