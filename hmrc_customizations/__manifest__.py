# -*- coding: utf-8 -*-
{
    'name': 'HMRC Customisations',
    'summary': "Extensions to integrate with UK HMRC system",
    'category': 'Payroll',
    'version': "1.0",
    'depends': ['taxation_integration_erpify', 'notifications_erpify', 'hr_payroll_community'],
    'author': 'ERPify Inc.',
    'company': 'ERPify Inc.',
    'website': "https://www.erpify.biz",
    'data': [
        'views/company_view.xml',
        'views/contract_view.xml',
        'views/employee_view.xml',
        'views/configuration_view.xml',
        'views/payslip_views.xml',
    ],
    'demo': ['data/tax_system_demo.xml'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
