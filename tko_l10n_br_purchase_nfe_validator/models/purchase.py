# -*- encoding: utf-8 -*-
from openerp import fields, api,models, _

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    supplier_product_name = fields.Char('Supplier Porudct', compute='get_product_name_for_supplier')
    supplier_product_code = fields.Char('Supplier Porudct', compute='get_product_name_for_supplier')


    def get_product_name_for_supplier(self):
        for record in self:
            supplier = record.order_id.partner_id
            product_name = record.product_id.name
            product_code = False
            for line in record.product_id.seller_ids:
                if line.name == supplier and line.product_name:
                    product_name = line.product_name
                    product_code = line.product_code
                    break
            record.supplier_product_name = product_name
            record.supplier_product_code = product_code


