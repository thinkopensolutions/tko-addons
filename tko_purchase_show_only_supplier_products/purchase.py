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

from openerp import models, fields, api, _


class purcahse_order_line(models.Model):
    _inherit = 'purchase.order.line'

    def onchange_product_id(
            self,
            cr,
            uid,
            ids,
            pricelist_id,
            product_id,
            qty,
            uom_id,
            partner_id,
            date_order=False,
            fiscal_position_id=False,
            date_planned=False,
            name=False,
            price_unit=False,
            state='draft',
            context=None):
        """
        onchange handler of product_id.
        """
        supplier_obj = self.pool.get('product.supplierinfo')
        product_obj = self.pool.get('product.product')
        res = super(
            purcahse_order_line,
            self).onchange_product_id(
            cr,
            uid,
            ids,
            pricelist_id,
            product_id,
            qty,
            uom_id,
            partner_id,
            date_order=date_order,
            fiscal_position_id=fiscal_position_id,
            date_planned=date_planned,
            name=name,
            price_unit=price_unit,
            state=state,
            context=context)
        product_ids = []
        if partner_id:
            # search all rows in supplierinfo with current partner
            supplier_ids = supplier_obj.search(
                cr, uid, [('name', '=', partner_id)])
            # get product_template_id
            template_ids = [
                supplier.product_tmpl_id.id for supplier in supplier_obj.browse(
                    cr, uid, supplier_ids)]
            # get product_ids
            product_ids = product_obj.search(
                cr, uid, [('product_tmpl_id', 'in', template_ids)])
        res.update({'domain': {'product_id': [('id', 'in', product_ids)]}})
        return res
