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
from openerp import fields, models, api
from openerp.exceptions import Warning


class poline_info(models.TransientModel):
    _name = 'poline.info'

    product_name = fields.Char('Product Name')
    product_qty = fields.Float('Qty')
    product_uom = fields.Many2one('product.uom', 'UoM')
    unit_price = fields.Float('Unit Price')
    tax_ids = fields.Many2many('account.tax', 'tax_poline_info_wizrd_rel', 'tax_id', 'wizard_id', 'Taxes')
    wizard_id = fields.Many2one('nfe.attachment.wizard', 'Wizard', delete='cascade')


class xml_line_info(models.TransientModel):
    _name = 'xml.line.info'

    product_name = fields.Char('Product Name')
    product_qty = fields.Float('Qty')
    product_uom = fields.Many2one('product.uom', 'UoM')
    unit_price = fields.Float('Unit Price')
    tax_ids = fields.Many2many('account.tax', 'tax_xml_info_wizrd_rel', 'tax_id', 'wizard_id', 'Taxes')
    wizard_id = fields.Many2one('nfe.attachment.wizard', 'Wizard', delete='cascade')


class nfeAttachmentWizard(models.TransientModel):
    _inherit = 'nfe.attachment.wizard'

    show_difference = fields.Boolean("Show Difference")
    correct_po_from_xml = fields.Boolean(
        u"Quer aceitar e corrigir o pedido de compra ou cancelar a importação e solicitar correção ao fornecedor?")
    po_line_info = fields.One2many('poline.info', 'wizard_id', 'PO Line Info')
    xml_line_info = fields.One2many('xml.line.info', 'wizard_id', 'PO Line Info')

    @api.multi
    def import_nfe_xml(self):
        context = dict(self._context)
        invoice = super(nfeAttachmentWizard, self).import_nfe_xml()
        if context.get('active_model', False) == 'purchase.order' and context.get('active_id', False):
            # write wizard ID in PO so that it can open same wizard next time
            self.env['purchase.order'].browse(self.active_id).write({'wizard_id': self.id})

        if invoice:
            if self.active_model == 'purchase.order' and self.active_id:
                po = self.env['purchase.order'].browse(self.active_id)
                for inv_line in invoice.invoice_line:
                    for pol in po.order_line:
                        # get matching inv line
                        if pol.product_id == inv_line.product_id and float(pol.product_qty) == float(
                                inv_line.quantity) and inv_line.uos_id == pol.product_uom:
                            pol.write({'invoiced': True, 'invoice_lines': [(4, inv_line.id)]})
                            break
                    else:
                        raise Warning("Please check PO Lines")
                # set invoice id in po
                po.write({'invoice_ids': [(4, invoice.id)]})
                return invoice
        if context.get('active_model', False) in ['purchase.order',
                                                  'nfe.attachment.wizard'] and self.id or self.active_model == 'purchase.order' and self.active_id:
            return {
                'name': 'Import NFe XML',  # form_view_id
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'nfe.attachment.wizard',
                'context': "{'model' : 'purchase.order'}",
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'res_id': self.id,
            ##please replace record_id and provide the id of the record to be opened  False to open new wizard
            }

    @api.one
    def cancel_po_picking(self):
        if self.active_model == 'purchase.order' and self.active_id:
            po = self.env['purchase.order'].browse(self.active_id)
            po.action_cancel()
