# -*- coding: utf-8 -*-
{
    'name': 'Claims Management',
    'version': '1.0',
    'website': 'https://www.odoo.com',
    'category': 'Customer Relationship Management',
    'description': """
Manage Customer Claims.
=======================
This application allows you to track your customers/suppliers claims and grievances.

It is fully integrated with the email gateway so that you can create
automatically new claims based on incoming emails.""",
    'depends': ['sales_team', 'base', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/crm_schedule_phonecall.xml',
        'views/crm_claim_view.xml',
        'views/crm_claim_menu.xml',
        'report/crm_claim_report_view.xml',
        'views/res_partner_view.xml',
        'views/crm_phonecall_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
