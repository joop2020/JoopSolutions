{
    'name': 'JJM: Joop Solutions Custom',
    'summary': '''Joop Solutions Custom''',
    'description': '''
Joop Solutions Custom
======================
        ''',
    'author': 'JJM',
    'email': 'admin@jjm.mx',
    'category': 'Custom Development',
    'version': '19.0.0.1.0',
    'depends': [
        'base',
        'purchase',
        'account',
        'l10n_mx_edi',
    ],
    'data': [
        'views/res_partner_inherit_views.xml',
        'views/account_move_views.xml',
    ],
    'license': 'LGPL-3',
    'application': True,
    'installable': True
}
