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

# from openerp.osv import osv, fields
from openerp import fields, api, models
from openerp.exceptions import Warning


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Validate condition on confirmation of order
    @api.multi
    def wkf_confirm_order(self):
        self.with_context(warn=True).get_valid_order()
        return super(PurchaseOrder, self).wkf_confirm_order()

    @api.one
    @api.depends('partner_id', 'order_line.product_id', 'order_line.product_qty', 'order_line.price_unit', 'order_line')
    def get_valid_order(self):
        self.valid_order = False
        context = self._context
        if self.partner_id.min_purchase_value <= self.amount_total:
            self.valid_order = True
        else:
            if context.get('warn', False):
                raise Warning(u'Order total is less than allowed for supplier!')

    valid_order = fields.Boolean(compute=get_valid_order, string="Is Visible", default=False)
