{
    'name': 'JJM: Syscom API Connector',
    'summary': 'Conexión básica con el API de SYSCOM (OAuth2) y consulta de productos',
    'description': '''
Syscom API Connector
====================
Capa de conexión con el API de SYSCOM (https://developers.syscom.mx/api/v1/).

- Autenticación OAuth2 (client_credentials) con cacheo de token.
- Servicio reutilizable para hacer peticiones a cualquier recurso del API.
- Asistente para probar la conexión y explorar la información de productos
  (búsqueda, detalle, categorías, marcas, tipo de cambio).

El enlace con product.template / product.product se construirá sobre esta capa
en una segunda etapa.
    ''',
    'author': 'JJM',
    'email': 'admin@jjm.mx',
    'category': 'Custom Development',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'base_setup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'wizard/syscom_test_views.xml',
    ],
    'installable': True,
    'application': False,
}