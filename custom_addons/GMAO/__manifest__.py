# GMAO/__manifest__.py

{
    'name': 'GMAO',
    'version': '1.0',
    'depends': ['maintenance'],
    'summary': 'Gestion de Maintenance Assitée par Ordinateur',
    'sequence':'1',
    'description': 'This module helps in the process of maintenance management',
    'author': 'Farah Safsafi',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_view.xml',
        'views/testview.xml',
        'views/request.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
