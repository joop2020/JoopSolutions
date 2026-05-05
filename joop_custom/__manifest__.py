{
    'name': 'JJM: Joop Solutions Custom',
    'summary': '''Joop Solutions Custom''',
    'description': '''
Joop Solutions Custom
======================
- Tipos de proyecto configurables
- Creación de proyectos desde CRM
- Creación de órdenes de compra desde tareas
        ''',
    'author': 'JJM',
    'email': 'admin@jjm.mx',
    'category': 'Custom Development',
    'version': '19.0.0.7.1',
    'depends': [
        'base',
        'purchase',
        'account',
        'l10n_mx_edi',
        'helpdesk',
        'crm',
        'project',
        'project_purchase',
        'sale_stock',
        'sale_crm',
        'product',
        'industry_fsm_report',
        'base_automation',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/joop_equipment_type_data.xml',
        'data/joop_fsm_worksheet_template.xml',
        'views/project_type_views.xml',
        'views/crm_lead_views.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/purchase_order_views.xml',
        'views/purchase_order_line_report_views.xml',
        'views/res_partner_inherit_views.xml',
        'views/account_move_views.xml',
        'views/report_invoice.xml',
        'views/report_deliveryslip.xml',
        'views/ticket_type_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/product_template_views.xml',
    ],
    'license': 'LGPL-3',
    'application': True,
    'installable': True
}
