{
    'name': 'Taxation Management',
    'version': '13.0.0.4',
    'category': 'Payroll',
    'summary': 'Base extensions to connect Odoo entities with 3rd party tax systems',
    "description": "",
    'author': 'ERPify Inc.',
    'website': 'http://www.erpify.biz',
    'depends': ['base', 'hr'],
    'data': [
            'views/company_view.xml',
            'security/ir.model.access.csv'
             ],
    'demo': ['data/tax_system_demo.xml'],    
    'installable': True,
    'auto_install': False,
}
