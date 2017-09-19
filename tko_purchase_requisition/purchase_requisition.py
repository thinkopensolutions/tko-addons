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

from odoo import models, fields, api, _
from openerp.exceptions import Warning


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    quantity_bid = fields.Float('Quantity Bid', help="Technical field for not loosing the initial information about the quantity proposed in the bid")

    @api.one
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.one
    def action_confirm(self):
        if not self.quantity_bid:
            self.quantity_bid = self.product_qty
        self.write({'state':'purchase'})


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    parent_id = fields.Many2one('purchase.requisition', string='Merged Into', readonly=True)
    child_ids = fields.One2many('purchase.requisition', 'parent_id', 'Children')

    def check_valid_quotation(self, quotation):
        for line in quotation.order_line:
            if line.state != 'purchase' or line.product_qty != line.quantity_bid:
                return False
        return True

    def _prepare_po_from_tender(self, tender,):
        return {'order_line': [], 'requisition_id': tender.id, 'origin': tender.name}

    def _prepare_po_line_from_tender(self, tender, line, purchase_id):
        return {'product_qty': line.quantity_bid, 'order_id': purchase_id.id}

    @api.model
    def generate_po(self, requisition_id):
        po = self.env['purchase.order']
        if requisition_id:
            requisition_id = self.browse(requisition_id)
            po_line_ids = []
            for x in requisition_id.purchase_ids:
                for line in x.order_line:
                    po_line_ids.append(line)
            id_per_supplier = {}
            confirm = False
            if requisition_id.state == 'done':
                raise Warning (_('You have already generate the purchase order(s).'))
            for po_line in po_line_ids:
                if po_line.state == 'purchase':
                    confirm = True
                    break
            if not confirm:
                raise Warning (_('You have no line selected for buying.'))
            for quotation in requisition_id.purchase_ids:
                if (self.check_valid_quotation(quotation)):
                    # use workflow to set PO state to confirm
                    quotation.button_confirm()
#  
            # get other confirmed lines per supplier
            for po_line in po_line_ids:
                # only take into account confirmed line that does not belong to already confirmed purchase order
                if po_line.state == 'purchase' and po_line.order_id.state in ['draft', 'sent', 'bid']:
                    if id_per_supplier.get(po_line.partner_id.id):
                        id_per_supplier[po_line.partner_id.id].append(po_line)
                    else:
                        id_per_supplier[po_line.partner_id.id] = [po_line]
#  
             # generate po based on supplier and cancel all previous RFQ
            for supplier, product_line in id_per_supplier.items():
                # copy a quotation for this supplier and change order_line then validate it
                quotation_id = po.search([('requisition_id', '=', requisition_id.id), ('partner_id', '=', supplier)], limit=1)[0]
                vals = self._prepare_po_from_tender(requisition_id)
                new_po = quotation_id.copy(default=vals)
                # duplicate po_line and change product_qty if needed and associate them to newly created PO
                for line in product_line:
                    vals = self._prepare_po_line_from_tender(requisition_id, line, new_po)
                    line.copy(default=vals)
                # use workflow to set new PO state to confirm

                new_po.button_confirm()

#             # cancel other orders
            self.cancel_unconfirmed_quotations(requisition_id)
#  
#             # set tender to state done
            requisition_id.action_done()
        return True

    def cancel_unconfirmed_quotations(self, tender):
        # cancel other orders
        po = self.pool.get('purchase.order')
        for quotation in tender.purchase_ids:
            if quotation.state in ['draft', 'sent', 'bid']:
                quotation.button_cancel()
                quotation.message_post(body='Cancelled by the call for bids associated to this request for quotation.')
        return True

    @api.multi
    def view_product_line(self):
        res = self.env.ref('tko_purchase_requisition.purchase_line_tree')
        lst = []
        for x in self.purchase_ids:
            for line in x.order_line:
                lst.append(line)
        if res:
           return {
               'name': _('Bid Lines'),
               'type': 'ir.actions.act_window',
               'view_type': 'form',
               'view_mode': 'tree',
               'target' : 'current',
               'domain':[('id', 'in', [line.id for line in lst])],
               'res_model': 'purchase.order.line',
               'context': {
                            'search_default_hide_cancelled':True,
                            'search_default_groupby_product':True,
                             'record_id':self.id
                            }
               }
        return res

    @api.multi
    def send_mail_to_all_quotations(self):
        template_id = self.env.ref('purchase.email_template_edi_purchase')
        if template_id:
            for rfq in self.purchase_ids:
                if rfq.partner_id.email:
                    values = template_id.generate_email(rfq.id)
                    values['email_to'] = rfq.partner_id.email
                    values['email_from'] = self.env.user.email
                    mail = self.env['mail.mail'].create(values)
                    attachment_ids = []
                    # create attachments
                    for attachment in values['attachments']:
                        attachment_data = {
                            'name': attachment[0],
                            'datas_fname': attachment[0],
                            'datas': attachment[1],
                            'res_model': 'mail.message',
                            'res_id': mail.mail_message_id.id,
                        }
                        attachment_ids.append(self.env['ir.attachment'].create(attachment_data).id)
                    if attachment_ids:
                        mail.write({'attachment_ids': [(6, 0, attachment_ids)]})
                    # send mail
                    mail.send()
                    # change status of RFQ
                    rfq.state = 'sent'
        return True
