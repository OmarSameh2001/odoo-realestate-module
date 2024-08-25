{
    'name': 'First App',
    'author': 'Omar Sameh',
    'version': '17.0.1.0.0',
    'category': '',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/base_menu.xml',
        'views/property_view.xml',
        'views/owner_view.xml',
        'views/sale_order_view.xml',
        'wizards/property_wizard_view.xml',
        'reports/property_report.xml',
        'data/sequence_view.xml',
    ],
    'application': True,
}
