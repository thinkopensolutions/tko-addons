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

from openerp import models, api, fields, _
from openerp.osv import osv


class res_compamy(models.Model):
    _inherit = 'res.company'

    average_federal_tax = fields.Float(
        'Average Federal Tax [%]',
        company_dependent=True,
        help='The average federal tax percentage [0..100]')
    average_state_tax = fields.Float(
        'Average State Tax Value [%]',
        company_dependent=True,
        help='The average state tax percentage [0..100]')
    order_reference = fields.Selection([('uid',u'Ref do Recibo'),('order',u'Referência da Ordem ')], string='Fiscal cupom reference', help="Selected option will be printed on fiscal cupom")
