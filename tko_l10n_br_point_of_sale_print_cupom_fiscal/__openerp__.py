# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
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
    'name': 'Point of Sale Print Receipt',
    'version': '0.108',
    'description': 'Point of Sale Print Receipt',
    'category': 'Customizations',
    'sequence': 150,
    'complexity': 'pos_customization',
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.tkobr.com',
    'images': ['images/oerp61.jpeg',
               ],
    'depends': [
        'point_of_sale',
        'tko_l10n_br_base',
        'tko_l10n_br_point_of_sale',
        'tko_point_of_sale_combined_categories_discount',
        # this module sets discount type fixed, used to compute fixed discount
        'tko_point_of_sale_discount_cards',
        # this module computes discount on total used for print
    ],

    'data': [
        'security/ir.model.access.csv',
        'static/src/xml/main.xml',
        'point_of_sale_view.xml',
        'account_tax_view.xml',
    ],
    'qweb': [
        'static/src/xml/printer.xml',
        'static/src/xml/pos.xml',
    ],
    'init': [],
    'demo': [],
    'update': [],
    'test': [],  # YAML files with tests
    'installable': True,
    'application': False,
    # If it's True, the modules will be auto-installed when all dependencies
    # are installed
    'auto_install': False,
    'certificate': '',
}
