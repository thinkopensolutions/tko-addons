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

class product_supplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    min_purchase_value = fields.Float(string="Minimum Purchase Amount")
    is_flexible = fields.Boolean(string="Is Flexible?")

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	def is_visible(self):
		flag = True
		for line in self.order_line:
			for supplier in line.product_id.seller_ids:
				if supplier.name.id == self.partner_id.id:
					if flag:
						if ((supplier.is_flexible == False) and (line.price_subtotal < supplier.min_purchase_value)):
							flag = False
		self.is_visible = flag

	is_visible = fields.Boolean(compute=is_visible,string="Is Visible", default=True)
