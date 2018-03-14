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
from odoo import fields, models, api
from openerp.exceptions import Warning


class PurchaseRequisitionWizard(models.TransientModel):
    _name = 'purchase.requisition.wizard'

    requisition_order_ids = fields.Many2many('purchase.requisition', 'requisition_order_merge_wizard_rel', 'wizard_id',
                                             'requisition_id', string='Requisition Orders')

    @api.model
    def default_get(self, fields):
        res = super(PurchaseRequisitionWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['requisition_order_ids'] = [(6, 0, active_ids)]
        return res

    @api.multi
    def validate_requisition_orders(self):
        invalid_orders = []
        for order in self.requisition_order_ids:
            if order.state != 'draft':
                invalid_orders.append(order.name)
        return invalid_orders

    @api.multi
    def merge_requisition_orders(self):
        self.ensure_one()
        invalid_orders = self.validate_requisition_orders()
        if len(invalid_orders):
            raise Warning("%s orders not in Draft stage" % invalid_orders)
        requisition_line_vals = {}
        for order in self.requisition_order_ids:
            for line in order.line_ids:
                uom_id = line.product_uom_id.id or False
                if line.product_id.id not in requisition_line_vals.keys():
                    requisition_line_vals.update({line.product_id.id: (line.product_qty, uom_id)})
                else:
                    requisition_line_vals[line.product_id.id] = (requisition_line_vals[
                                                                     line.product_id.id][0] + line.product_qty, uom_id)
        # create requisition_order
        order = self.requisition_order_ids[0].sudo().copy(default={'line_ids': False})
        for product_id, qty_uom in requisition_line_vals.iteritems():
            self.env['purchase.requisition.line'].create(
                {'product_id': product_id, 'product_qty': qty_uom[0], 'requisition_id': order.id,
                 'product_uom_id': qty_uom[1]})
        # cancel selected orders
        self.requisition_order_ids.write({'parent_id': order.id})
        # cancel orders
        for tender in self.requisition_order_ids:
            tender.action_cancel()
        model, view_id = self.env['ir.model.data'].get_object_reference('purchase_requisition',
                                                                        'view_purchase_requisition_form')
        # return target form
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.requisition',
            'res_id': order.id,
            'view_type': 'form',
        }
