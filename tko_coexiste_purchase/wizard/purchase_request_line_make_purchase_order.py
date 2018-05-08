# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

import odoo.addons.decimal_precision as dp
from odoo import _, api, exceptions, fields, models


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"
    _description = "Purchase Request Line Make Purchase Order"


    # Set origin in the created PO
    @api.model
    def _prepare_purchase_order(self, picking_type, location, company):
        active_id = self._context.get('active_id',False)

        data = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order(picking_type, location, company)
        if active_id:
            line = self.env['purchase.request.line'].browse(active_id)
            if line.request_id:
                data.update({'origin': line.request_id.origin})
        return data

