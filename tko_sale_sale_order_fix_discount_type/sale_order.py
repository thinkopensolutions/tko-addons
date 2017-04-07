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
import openerp.addons.decimal_precision as dp
from openerp import fields, api, models
from openerp.osv import fields as fields_v7


class sale_order(models.Model):
    _inherit = 'sale.order'

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_discount': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            cur = order.pricelist_id.currency_id
            val1 = val2 = val3 = 0.0
            for line in order.order_line:
                val1 += line.price_subtotal
                val2 += self._amount_line_tax(cr, uid, line, context=context)
                val3 += (line.product_uom_qty * line.price_unit) * line.discount / 100
            res[order.id]['amount_untaxed'] = round(cur_obj.round(cr, uid, cur, val1))
            res[order.id]['amount_tax'] = round(cur_obj.round(cr, uid, cur, val2))
            res[order.id]['amount_discount'] = round(cur_obj.round(cr, uid, cur, val3))
            res[order.id]['amount_total'] = round(res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'])
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'discount_type': fields_v7.selection([
            ('percent', 'Percentage'),
            ('amount', 'Amount')], 'Discount type'),
        'discount_rate': fields_v7.float('Discount Rate', digits_compute=dp.get_precision('Account'),
                                         readonly=True,
                                         states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, ),
        'amount_discount': fields_v7.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                              string='Discount',
                                              multi='sums', store=True, help="The total discount."),
        'amount_untaxed': fields_v7.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                             string='Untaxed Amount',
                                             multi='sums', store=True, help="The amount without tax.",
                                             track_visibility='always'),
        'amount_tax': fields_v7.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
                                         multi='sums', store=True, help="The tax amount."),
        'amount_total': fields_v7.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
                                           multi='sums', store=True, help="The total amount."),
    }

    _defaults = {
        'discount_type': 'percent',
    }

    @api.multi
    def compute_discount(self, discount):
        for order in self:
            val1 = val2 = 0.0
            disc_amnt = 0.0
            for line in order.order_line:
                val1 += (line.product_uom_qty * line.price_unit)
                line.discount = discount
                line.discount_value = discount
                val2 += self._amount_line_tax(line)
                disc_amnt += (line.product_uom_qty * line.price_unit * line.discount) / 100
            total = val1 + val2 - disc_amnt
            self.currency_id = order.pricelist_id.currency_id
            self.amount_discount = round(disc_amnt)
            self.amount_tax = round(val2)
            self.amount_total = round(total)

    @api.onchange('discount_type', 'discount_rate')
    def supply_rate(self):
        for order in self:
            if order.discount_type == 'percent':
                self.compute_discount(order.discount_rate)
            else:
                total = 0.0
                for line in order.order_line:
                    total += (line.product_uom_qty * line.price_unit)
                discount = (order.discount_rate / total) * 100
                self.compute_discount(discount)


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    discount = fields.Float('Discount (%)', digits_compute=dp.get_precision('Payment Term'), readonly=True,
                            states={'draft': [('readonly', False)]})
    discount_type = fields.Selection([('fi', 'Fixed'), ('p', 'Percent')], default='p', required=True,
                                     string='Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)]})
    discount_value = fields.Float('Discount', readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('discount_type', 'discount_value', 'product_uom_qty', 'price_unit')
    def onchange_discount_type(self):
        res = {'value': {}}
        if self.discount_type == 'p':
            self.discount = self.discount_value
        else:
            try:
                price = self.product_uom_qty * self.price_unit
                self.discount = 100 - (price - self.discount_value) * 100 / price
            except:
                self.discount = 0

    # set discount
    @api.model
    def _clone_discount_from_sale_order_lines(self):
        self._cr.execute("update sale_order_line set discount_value= discount")
        return True
