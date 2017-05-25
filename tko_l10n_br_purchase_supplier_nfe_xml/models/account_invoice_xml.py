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

from openerp import models, fields, api, _

class account_invoice_xml_form(models.Model):
    _name = "account.invoice.xml.form"
    _rec_name = 'invoice_num'
    
    supplier = fields.Char(string='Supplier', readonly=True)
    invoice_date = fields.Date(string="Invoice Date", readonly=True)
    invoice_due_date = fields.Date(string="Invoice Due Date", readonly=True)
    invoice_num = fields.Char(string="Invoice Number", readonly=True)
    total =fields.Float(string="Total", readonly=True)
    invoice_line_xml_ids = fields.One2many('account.invoice.line.xml', 'invoice_line_xml_id', 'Invoice Xml Lines')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, 
        default=lambda self: self.env['res.company']._company_default_get('account.invoice.xml.form'))
    currency_id = fields.Many2one(related='company_id.currency_id', string='Currency')

class account_invoice_line_xml(models.Model):
    _name = 'account.invoice.line.xml'

    product = fields.Char(string='Product', readonly=True)
    qty = fields.Char(string="Quantity", readonly=True)
    uom = fields.Char(string="UOM", readonly=True)
    unit_price = fields.Float(string='Unit Price', readonly=True)
    total = fields.Char(string="Total", readonly=True)
    invoice_line_xml_id = fields.Many2one('account.invoice.xml.form',string="Invoice XML")
