# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _


class Orderpoint(models.Model):
    """ Defines Minimum stock rules. """
    """
    Defines Minimum stock rules.
    """
    _inherit = "stock.warehouse.orderpoint"
    _description = "Minimum Inventory Rule"

    qty_available = fields.Boolean(string='Subtract Quantity On Hand', default=True)

    @api.multi
    def subtract_procurements_from_orderpoints(self):
        res = super(Orderpoint, self).subtract_procurements_from_orderpoints()
        for rec in self:
            if res.get(rec.id):
                res.update({rec.id: (res.get(rec.id) + rec.product_id.qty_available)})
        return res
