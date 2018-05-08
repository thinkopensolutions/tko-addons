# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.model
    def create(self, vals):
        if 'name' in vals.keys() and vals['name']:
            vals.update({'origin' : vals['name']})
        return super(PurchaseRequest, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'name' in vals.keys() and vals['name']:
            vals.update({'origin': vals['name']})
        return super(PurchaseRequest, self).write(vals)