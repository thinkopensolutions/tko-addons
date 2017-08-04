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

from openerp import models, fields, api


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    parent_id = fields.Many2one('purchase.requisition', string='Merged Into', readonly=True)
    child_ids = fields.One2many('purchase.requisition','parent_id','Children')


    @api.multi
    def send_mail_to_all_quotations(self):
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase')[1]
        if template_id:
            for rfq in self.purchase_ids:
                if rfq.partner_id.email and rfq.state == 'draft':
                    template_obj = self.env['email.template']
                    values = template_obj.generate_email(template_id, rfq.id)
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
                    rfq.signal_workflow('send_rfq')
        return True

    @api.multi
    def open_product_line(self):
        po_line_obj = self.env['purchase.order.line']
        res = super(PurchaseRequisition, self).open_product_line()
        if res and res.get('domain'):
            if res.get('domain')[0] and res.get('domain')[0][2]:
                po_line_ids = res.get('domain')[0][2]
                #Before update all lines.
                purchase_line_rec = po_line_obj.browse(po_line_ids)
                purchase_line_rec.write({'is_lowest_price': False})
                self._cr.execute('''SELECT product_id FROM purchase_order_line
                                    WHERE id in (%s) GROUP BY product_id
                                ''' %(','.join(map(str, po_line_ids))))
                datas = [line[0] for line in self._cr.fetchall()]
                if datas:
                    for line_id in datas:
                        self._cr.execute('''SELECT id FROM purchase_order_line
                                            WHERE id in (%s)
                                            AND product_id = %s ORDER BY price_unit*product_qty ASC LIMIT 1
                                        ''' %(','.join(map(str, po_line_ids)), line_id))
                        datas_po_line = self._cr.fetchone()
                        if datas_po_line:
                            po_line_rec = po_line_obj.browse(datas_po_line[0])
                            po_line_rec.write({'is_lowest_price': True})
        return res
