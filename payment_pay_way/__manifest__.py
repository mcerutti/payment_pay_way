# -*- coding: utf-8 -*-
{
    'name': "Payway payment Acquirer",
    'summary': """
        Payway payment Acquirer
        (formely Decidir 2.0)
    """,
    'description': """
        Payway payment Acquirer
        (formely Decidir 2.0)
    """,
    'author': 'ADHOC SA - Axcelere S.A.S - Matias Cerutti',
    'website': 'www.adhoc.com.ar, www.axcelere.com',
    'category': 'Accounting/Payment Acquirers',
    'version': '15.0.1.0.1',
    'images':  ['static/description/thumb.png'],
    'depends': ['payment', 'card_installment', 'account_debit_note'],
    'assets': {
        'web.assets_frontend': [
            'payment_pay_way/static/src/js/payway.js',
            'https://live.decidir.com/static/v2.5/decidir.js',
            'https://cdnjs.cloudflare.com/ajax/libs/imask/3.4.0/imask.min.js',
            'payment_pay_way/static/src/css/ccform.scss',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/payment_acquirer.xml',
        'views/templates.xml',
        'views/account_card.xml',
        'views/payment_transaction.xml',
        'data/payment_acquirer_data.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
