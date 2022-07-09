# -*- coding: utf-8 -*-
{
    'name': 'Consulta CUIT',
    'version': '15.0',
    'summary': """Consulta CUIT""",
    'description': 'Consulta y rellena campos del partner mediante la API de Tango. Verifica que exista un solo partner por N° de identificación (VAT/CUIT/CUIL/DNI)',
    "category": "Partner",
    'author': 'Bisiach Lucio',
    'company': 'Bisiach Lucio',
    'website': "",
    'depends': ['l10n_ar'],
    'data': [
        'views/res_partner.xml'
    ],
    'images': [],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}