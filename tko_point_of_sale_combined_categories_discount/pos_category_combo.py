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
from openerp import fields, models, api, _

from openerp.osv import osv, fields as fieldsv7

class pos_category_combo(models.Model):
    _name = 'pos.category.combo'
    
    main_category_id = fields.Many2one('pos.category', 'Main Category', required=True)
    disc_category_id = fields.Many2one('pos.category', 'Discount Category', required=True)
    type = fields.Selection([('p', 'Percentage'), ('fi', 'Fixed')], string='Type', required=True)
    value = fields.Float('Value', required=True)
    
    _sql_constraints = [('category_combo_unique', 'unique(main_category_id, disc_category_id)', _('You already have a combo with current selected categories')),]
    

#adding field becuase we need to have values of combo ids even if no internet connection   

class pos_session(models.Model):
    _inherit = 'pos.session'
    
    combo_ids = fields.Many2many('pos.category.combo','session_combo_rel','session_id', related='config_id.combo_ids', string='Combo Discount')
     

class pos_config(models.Model):
    _inherit = 'pos.config'
    
    combo_ids = fields.Many2many('pos.category.combo','config_combo_rel','config_id', 'combo_id',  compute='get_category_combo_ids', string='Combo Discount')
    
    def get_category_combo_ids(self):
        for records in self:
            combo_ids = self.env['pos.category.combo'].search([])
            records.combo_ids = [(6 , 0 , [combo_id.id for combo_id in combo_ids])]


class pos_order_line(models.Model):
    _inherit = 'pos.order.line'
    
    discount_type = fields.Selection([('f', 'Fixed'), ('p', 'Percentage')], string='Discount Type', default='p')
    discount_value = fields.Float('Discount')
    
   
    @api.onchange('discount_type', 'discount_value','qty','price_unit')
    def change_discount(self):
        discount_type = self.discount_type or 'p'
        discount = self.discount_value or 0.0
        qty = self.qty
        price_unit = self.price_unit
        if discount_type == 'f':
            self.discount = discount * 100 / (price_unit * qty)
        else:
            self.discount = discount
   
    @api.model
    def create(self, vals):
        discount = vals.get('discount', 0.0)
        discount_type = vals.get('discount_type',False)
        qty = vals.get('qty', 0.0)
        price_unit = vals.get('price_unit', 0.0)
        vals.update({'discount_value' : discount})
        if discount_type and discount_type == 'fi':
            discount = discount * 100 / (price_unit * qty)
            vals.update({'discount' : discount, 'discount_type' : 'f'})
        res = super(pos_order_line,self).create(vals)
        return res
    
    
## code to be removed
#we chn remove this class we wil lnot need this its just to re compute all wrong orders
class pos_order_line(osv.osv):
    _inherit = 'pos.order.line'
    
    def _amount_line_all(self, cr, uid, ids, field_names, arg, context=None):
        res = dict([(i, {}) for i in ids])
        account_tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context=context):
            taxes_ids = [ tax for tax in line.product_id.taxes_id if tax.company_id.id == line.order_id.company_id.id ]
            #compoute discount 
            discount_type = line.discount_type or 'p'
            discount = line.discount_value or 0.0
            qty = line.qty
            price_unit = line.price_unit
            if discount_type == 'f':
                discount = discount * 100 / (price_unit * qty)
            else:
                discount = discount
            
            price = line.price_unit * (1 - (discount or 0.0) / 100.0)
            taxes = account_tax_obj.compute_all(cr, uid, taxes_ids, price, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)

            cur = line.order_id.pricelist_id.currency_id
            res[line.id]['discount'] = discount
            res[line.id]['price_subtotal'] = cur_obj.round(cr, uid, cur, taxes['total'])
            res[line.id]['price_subtotal_incl'] = cur_obj.round(cr, uid, cur, taxes['total_included'])
        return res
    
    _columns ={
               'price_subtotal_incl': fieldsv7.function(_amount_line_all, multi='pos_order_line_amount', digits_compute=dp.get_precision('Account'), string='Subtotal w/o Tax', store=True),
               }




class pos_order(osv.osv):
    _inherit = 'pos.order'
    
    def validate_old_orders(self, cr, uid, ids, context = None):
        pos_obj = self.pool.get('pos.order')
        print "searching orders......................."
        order_ids = pos_obj.search(cr ,uid, [('state','=','draft')])
        print "orders found.............",order_ids, len(order_ids)
        if len(order_ids) > 100:
            order_ids= order_ids[0:99]
        for order_id in order_ids:
            if pos_obj.test_paid(cr, uid, [order_id]):
                    print "validating order_id..................",order_id
                    pos_obj.signal_workflow(cr, uid, [order_id], 'paid')
        return True
                        