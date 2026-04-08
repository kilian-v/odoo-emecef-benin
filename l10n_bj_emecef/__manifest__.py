# -*- coding: utf-8 -*-
{
    'name': "e-MECeF Bénin - Facturation Normalisée",

    'summary': "Intégration officielle de la facturation normalisée e-MECeF (DGI Bénin)",

    'description': """
        Ce module permet aux entreprises béninoises de normaliser leurs factures directement depuis Odoo.
        
        Fonctionnalités principales :
        - Connexion à l'API e-MECeF de la DGI Bénin
        - Normalisation des factures de vente (FV) et des avoirs (FA)
        - Génération automatique du Code MECeF et du QR Code
        - Impression du ticket/PDF de facture au format officiel DGI
        - Récupération automatique des informations clients via leur IFU
        - Gestion de la ventilation des taxes (A, B, C, D, E, F) et de l'AIB
    """,

    'author': "KV - Cashless Africa",
    'website': "https://cashless.africa",
    'maintainer': 'Cashless Africa',

    'category': 'Accounting/Localizations',
    'version': '1.0',
    'license': 'LGPL-3',

    'depends': ['base', 'account'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/emecef_confirm_wizard_views.xml',
        'views/res_company_views.xml',
        'views/account_tax_views.xml',
        'views/account_journal_views.xml',
        'views/res_partner_views.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/report_emecef.xml',
    ],

    'images': ['static/description/icon.png'],

    'demo': [
        'demo/demo.xml',
    ],

    'installable': True,
    'application': True,
}
