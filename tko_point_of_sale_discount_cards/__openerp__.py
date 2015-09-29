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
    'name': 'tko_point_of_sale_discount_cards',
    'version': '0.031',
    'description': 'This module applies selected discount on total',
    'category': 'Customizations',
    'sequence': 150,
    'complexity': 'pos_customization',
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.tkobr.com',
    'images': ['images/oerp61.jpeg',
              ],
    'depends': [
                'point_of_sale',
                'tko_point_of_sale_discount_on_order',
                ],
                
    'data': [
             'security/ir.model.access.csv',
             'point_of_sale_view.xml',
             'static/src/xml/pos.xml',
             ],
    'qweb' : ['static/src/xml/discount.xml',],
    'init': [],
    'demo': [],
    'update': [],
    'test': [], #YAML files with tests
    'installable': True,
    'application': False,
    'auto_install': False, #If it's True, the modules will be auto-installed when all dependencies are installed
    'certificate': '',
}
