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
    'name': 'tko_l10n_br_purchase_supplier_nfe_xml_import',
    'version': '0.006',
    'category': 'Localisation',
    'sequence': 38,
    'complexity': 'normal',
    'description': ''' DESCRIPTION TO BE CHANGED ''',
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.thinkopensolution.com.br',
    'images': ['images/oerp61.jpeg', ],
    'depends': [
        'l10n_br_purchase',
        'tko_l10n_br_account_invoice_nfe_xml_import',
    ],
    'data': [
        # 'purchase_workflow.xml',
        'purchase_view.xml',
        'nfe_attachment_view.xml',
        'stock_picking_view.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
    'certificate': '',
}
