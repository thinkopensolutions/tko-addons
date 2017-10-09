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
    'name': 'tko_point_of_sale_product_price_by_pos',
    'version': '0.009',
    'description': '''This module allows to create price exception for products by each POS
if Exception is defined for a pos, price from exception is considered in particular POS only''',
    'category': 'Customizations',
    'sequence': 150,
    'complexity': 'pos_customization',
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.tkobr.com',
    'images': ['images/oerp61.jpeg',
               ],
    'depends': [
        'point_of_sale',
        'tko_point_of_sale_combined_categories_discount'
        # add dependency becasue we are able to call super in single module in both it falls in Uncaught RangeError: Maximum call stack size exceeded
    ],

    'data': [
        'security/ir.model.access.csv',
        'pos_view.xml',
        'static/src/xml/pos.xml',
    ],
    'qweb': [
        'static/src/xml/pos_templates_view.xml',
    ],
    'init': [],
    'demo': [],
    'update': [],
    'test': [],  # YAML files with tests
    'installable': True,
    'application': False,
    'auto_install': False,  # If it's True, the modules will be auto-installed when all dependencies are installed
    'certificate': '',
}
