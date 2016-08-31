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
import logging

from openerp import fields, models, api, _
from openerp.osv import osv

_logger = logging.getLogger(__name__)


class pos_category_combo(models.Model):
    _name = 'pos.category.combo'

    main_category_id = fields.Many2one(
        'pos.category', 'Main Category', required=True)
    disc_category_id = fields.Many2one(
        'pos.category', 'Discount Category', required=True)
    type = fields.Selection(
        [('p', 'Percentage'), ('fi', 'Fixed')], string='Type', required=True)
    value = fields.Float('Value', required=True)
    company_id = fields.Many2one('res.company', string='Company')
    company_ids = fields.Many2many('res.company', string='Company')

    _sql_constraints = [
        ('category_combo_unique',
         'unique(main_category_id, disc_category_id,company_id)',
         _('You already have a combo with current selected categories')),
    ]


# adding field becuase we need to have values of combo ids even if no
# internet connection

class pos_session(models.Model):
    _inherit = 'pos.session'

    combo_ids = fields.Many2many(
        'pos.category.combo',
        'session_combo_rel',
        'session_id',
        related='config_id.combo_ids',
        string='Combo Discount')


class pos_config(models.Model):
    _inherit = 'pos.config'

    combo_ids = fields.Many2many(
        'pos.category.combo',
        'config_combo_rel',
        'config_id',
        'combo_id',
        compute='get_category_combo_ids',
        string='Combo Discount')

    def get_category_combo_ids(self):
        for records in self:
            combo_ids = self.env['pos.category.combo'].search(
                [('company_id', '=', records.company_id.id)])
            records.combo_ids = [
                (6, 0, [combo_id.id for combo_id in combo_ids])]


class pos_order_line(models.Model):
    _inherit = 'pos.order.line'

    discount_type = fields.Selection(
        [('fi', 'Fixed'), ('p', 'Percentage')], string='Discount Type', default='p')
    discount_value = fields.Float('Discounted Amount')

    @api.onchange('discount_type', 'discount_value', 'qty', 'price_unit')
    def change_discount(self):
        discount_type = self.discount_type or 'p'
        discount = self.discount_value or 0.0
        qty = self.qty
        price_unit = self.price_unit
        if discount_type == 'fi':
            try:
                self.discount = discount * 100 / (price_unit * qty)
            except:
                discount = 0.0
        else:
            self.discount = discount

    @api.model
    def create(self, vals):
        discount = vals.get('discount', 0.0)
        discount_type = vals.get('discount_type', False)
        qty = vals.get('qty', 0.0)
        price_unit = vals.get('price_unit', 0.0)
        vals.update({'discount_value': discount})
        if discount_type and discount_type == 'fi' and price_unit and qty:
            try:
                discount = discount * 100 / (price_unit * qty)
            except:
                discount = 0.0
            vals.update({'discount': discount, 'discount_type': 'fi'})
        res = super(pos_order_line, self).create(vals)
        return res


# This code below checks orders in 'New' Stage validates them with workflow
class pos_order(osv.osv):
    _inherit = 'pos.order'

    # this method corrects payment info based on total of order
    def validate_old_orders(self, cr, uid, ids, context=None):
        pos_obj = self.pool.get('pos.order')
        _logger.info("searching orders in new stage............")
        order_ids = pos_obj.search(cr, uid, [('state', '=', 'draft')])
        for order_id in order_ids:
            order_total = self.browse(cr, uid, order_id).amount_total
            payemnt_total = 0.0
            for statement_line in self.browse(cr, uid, order_id).statement_ids:
                payemnt_total = payemnt_total + statement_line.amount
            if payemnt_total != order_total:
                for statement_line in self.browse(
                        cr, uid, order_id).statement_ids:
                    self.pool.get('account.bank.statement.line').write(cr, uid, [statement_line.id], {
                        'amount': statement_line.amount - (payemnt_total - order_total)})
                    break
            if pos_obj.test_paid(cr, uid, [order_id]):
                _logger.info("seting order to Paid............%s" % (order_id))
                pos_obj.signal_workflow(cr, uid, [order_id], 'paid')
        return True
