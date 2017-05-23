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
from openerp import fields, api, models


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    wizard_id = fields.Integer('Wizard', copy=False)
    invoice_method = fields.Selection(
        [('manual', 'Based on Purchase Order lines'), ('order', 'Based on generated draft invoice'),
         ('picking', 'Based on incoming shipments')], 'Invoicing Control', required=True,
        readonly=True, default='manual',
        help="Based on Purchase Order lines: place individual lines in 'Invoice Control / On Purchase Order lines' from where you can selectively create an invoice.\n" \
             "Based on generated invoice: create a draft invoice you can validate later.\n" \
             "Based on incoming shipments: let you create an invoice when receipts are validated.")
    invoice_control = fields.Selection(
        [('manual', 'Based on Purchase Order lines'), ('picking', 'Based on incoming shipments')], 'Invoicing Control',
        required=True,
        readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, default='manual',
        help="Based on Purchase Order lines: place individual lines in 'Invoice Control / On Purchase Order lines' from where you can selectively create an invoice.\n" \
             "Based on incoming shipments: let you create an invoice when receipts are validated.")

    @api.onchange('invoice_control')
    def onchange_invoice_control(self):
        res = {}
        self.invoice_method = self.invoice_control

    @api.multi
    def import_supplier_nfe(self):
        wizard = self.env.ref("tko_l10n_br_account_invoice_nfe_xml_import.nfe_attachment_wizard")
        res_id = False
        if self.wizard_id:
            try:
                self.env['nfe.attachment.wizard'].browse(self.wizard_id).name
                res_id = self.wizard_id
            except:
                res_id = False
        return {
            'name': 'Import NFe XML',  # form_view_id
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': wizard.id or False,
            'res_model': 'nfe.attachment.wizard',
            'context': "{'model' : 'purchase.order'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'res_id': res_id,
        ##please replace record_id and provide the id of the record to be opened  False to open new wizard
        }
