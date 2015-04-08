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
    'name': 'Brasil - Plano de Contas ECD para Empresas de Serviços',
    'category': 'Localization/Account Charts',
    'description': "Plano de contas ECD Brasil para empresas de serviços.",
    'author': 'ThinkOpen Solutions Brasil',
    'license': 'AGPL-3',
    'website': 'http://tkobr.com',
    'version': '1.001',
    'sequence': 8,
    'depends': [
                'account',
                'account_chart',
                ],
    'data': [
             'data/account.account.csv',
             'data/account.account.template.csv',
             'data/account_chart_template.xml',
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

