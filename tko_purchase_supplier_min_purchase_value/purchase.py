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
        self.with_context(warn=True).get_is_visible()
        return super(PurchaseOrder, self).wkf_confirm_order()

    @api.depends('order_line.product_id', 'order_line.product_qty', 'order_line.price_unit')
    def get_is_visible(self):
        context = self._context or {}
        warn = context.get('warn', False)
        flag = True
        for line in self.order_line:
            for supplier in line.product_id.seller_ids:
                if supplier.name.id == self.partner_id.id:
                    if flag:
                        if ((supplier.is_flexible == False) and (line.price_subtotal < supplier.min_purchase_value)):
                            flag = False
                            if warn:
                                raise Warning(u'Price subtotal : %s for product %s is less than allowed value %s' % (
                                    line.price_subtotal, line.product_id.name, supplier.min_purchase_value))
        self.is_visible = flag

    is_visible = fields.Boolean(compute=get_is_visible, string="Is Visible", default=True)
