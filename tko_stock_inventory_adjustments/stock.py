# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class stock_inventory(models.Model):
    _name = 'stock.inventory.adjustments'
    _inherit = 'stock.inventory'
    _description = "Stock Inventory Adjustments"

class stock_inventory_line(models.Model):
    _name = 'stock.inventory.line.adjustments'
    _inherit = 'stock.inventory.line'
    _description = "Stock Inventory Line Adjustments"

    _columns = {
        # consumed quantity should be informed and substracted from theoretical quantity
        'consumed_qty': fields.float('Checked Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'theoretical_qty': fields.function(_get_theoretical_qty, type='float',
                                           digits_compute=dp.get_precision('Product Unit of Measure'),
                                           store={'stock.inventory.line': (lambda self, cr, uid, ids, c={}: ids,
                                                                           ['location_id', 'product_id', 'package_id',
                                                                            'product_uom_id', 'company_id',
                                                                            'prod_lot_id', 'partner_id'], 20), },
                                           readonly=True, string="Theoretical Quantity")
    }



# add the options for line creation?
