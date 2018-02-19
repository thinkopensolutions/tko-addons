# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'tko_coexiste_br_account',
    'version': '0.001',
    'category': 'Customizations',
    'sequence': 150,
    'description': '''  tko_coexiste_br_account''',
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.tkobr.com',
    'depends': [
        'base',
        'account',
        'br_account',
        'tko_account_moves_in_draft',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/account_expense_view.xml',
        'views/ir_attachment_view.xml',
        'views/account_analytic_view.xml',
        'views/account_view.xml',
        'views/account.xml',

    ],
    'init': [],
    'demo': [],
    'update': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'certificate': '',
}
