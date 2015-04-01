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
    'name': 'Layout Brasileiro da fatura com CNPJ/CPF',
    'version': '0.001',
    'category': 'Localisation',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''Este módulo adiciona o CNPJ/CPF, IE e telefone no relatório da fatura.''',
    'author': 'ThinkOpen Solutions Brasil',
    'license': 'AGPL-3',
    'website': 'http://www.tkobr.com',
    'depends': [
                'base',
                'account',
                'l10n_br_base',
                ],
    'data': [
             'views/report_invoice.xml',
             ],
    'installable': True,
    'application': False,
    'certificate': '',
}
