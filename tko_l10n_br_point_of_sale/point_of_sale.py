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
from openerp import models, api, fields, _

class pos_order(models.Model):
    _inherit = 'pos.order'
    
    # compute taxes with not tax.base_code_id.tax_discount
    def _amount_line_tax(self, cr, uid, line, context=None):
        account_tax_obj = self.pool['account.tax']
        #Do not sum taxes which have base_code_id.tax_discount set to True
        taxes_ids = [tax for tax in line.line_taxes_ids if tax.company_id.id == line.order_id.company_id.id and not tax.base_code_id.tax_discount]
        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        taxes = account_tax_obj.compute_all(cr, uid, taxes_ids, price, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)['taxes']
        val = 0.0
        for c in taxes:
            val += c.get('amount', 0.0)
        return val
    
    
    def create_from_ui(self, cr, uid, orders, context=None):
        # Keep only new orders

        pos_obj = self.pool.get('pos.order')
        pos_line_object = self.pool.get('pos.order.line')
        table_reserved_obj = self.pool.get("table.reserverd")
        session_obj = self.pool.get('pos.session')
        shop_obj = self.pool.get('sale.shop')
        partner_obj = self.pool.get('res.partner')
        company_taxes = [tax.tax_id.id for tax in self.pool.get('res.users').browse(cr, uid, uid).company_id.product_tax_definition_line]
      
        
        for tmp_order in orders:

            if 'data' in tmp_order.keys():
                for line in tmp_order['data']['lines']:
                    #product_id of line
                    if 'product_id' in line[2].keys():
                        product_id = line[2]['product_id']
                        product_taxes = [tax.id for tax in self.pool.get('product.product').browse(cr, uid, product_id).taxes_id]
                        taxes  = list(set(product_taxes + company_taxes))
                        line[2]['line_taxes_ids'] = [(6,0, taxes)]
        return super(pos_order, self).create_from_ui(cr, uid, orders, context=context)
    
class pos_order_line(models.Model):
    _inherit = 'pos.order.line'
    
    
    line_taxes_ids = fields.Many2many('account.tax', 'pos_line_tax_rel', 'order_line_id', 'tax_id', string=u'Taxes')
    
    def tko_onchange_product_id(self, cr, uid, ids, pricelist, product_id, qty=0, partner_id=False, context=None):
        result = self.onchange_product_id(cr, uid, ids, pricelist, product_id, qty=qty, partner_id=partner_id, context=context)
        user = self.pool.get('res.users').browse(cr, uid, uid)
        if 'value' in result.keys():
            line_taxes = [tax.id for tax in self.pool.get('product.product').browse(cr, uid, product_id).taxes_id]
            companny_taxes = []
            for comp_tax in user.company_id.product_tax_definition_line:
                companny_taxes.append(comp_tax.tax_id.id)
            total_taxes = list(set(companny_taxes + line_taxes))
            result['value']['line_taxes_ids'] = [(6, 0, total_taxes)]
        return result
    #===========================================================================
    # @api.multi
    # def product_id_change(self, product, uom, qty=0, name='', 
    #                       type='out_invoice', partner_id=False, 
    #                       fposition_id=False, price_unit=False, 
    #                       currency_id=False, company_id=None):
    #===========================================================================
