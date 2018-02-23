# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>

{
    'name': 'Eradicate Create & Create and Edit...',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'summary': 'Disable Create & Create and Edit on all objects',
    'description': """
Disables Create and Edit from all the models and fields
=========================================================

Disable quick create on all objects of Odoo.

This module has been written by Yogesh Kushwaha from TKO <yogesh@tkobr.com>.
    """,
    'author': 'TKO',
    'website': 'http://www.akretion.com',
    'depends': ['base'],
    'installable': True,
    'data': ['views/form_common_view.xml',]
}
