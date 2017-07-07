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
from openerp.osv import fields, osv
class stock_warehouse_orderpoint(osv.osv):
    """
    Defines Minimum stock rules.
    """
    _inherit = "stock.warehouse.orderpoint"
    _description = "Minimum Inventory Rule"

    _columns = {
     'qty_available' : fields.boolean(u'Subtract Quantity On Hand')
    }
    _defaults={
        'qty_available' : True
    }

    def subtract_procurements(self, cr, uid, orderpoint, context=None):
        '''This function returns quantity of product that needs to be deducted from the orderpoint computed quantity because there's already a procurement created with aim to fulfill it.
        '''
        qty = super(stock_warehouse_orderpoint, self).subtract_procurements(cr, uid, orderpoint, context=None)
        # add available product qty
        if orderpoint.qty_available:
            qty += orderpoint.product_id.qty_available
        return qty
