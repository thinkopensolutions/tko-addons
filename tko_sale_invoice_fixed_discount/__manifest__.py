{
    'name': 'Sale Discount',
    'version': '1.0',
    'category': 'sale',
    'summary': "Discount on total Sale",
    'author': 'ThinkOpen Solutions Brasil',
    'company': '',
    'website': 'http://www.tkobr.com',
    'description': """Module to manage discount on total amount in Sale as specific amount or percentage.""",
    'depends': ['sale','account'],
    'data': [
        'views/sale_view.xml',
        'views/account_invoice_view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
