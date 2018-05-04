# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class UpdateInvoiceLineWizard(models.TransientModel):
    _name = 'update.invoice.line.wizard'

    invoice_lines = fields.One2many('update.invoice.line.wizard.line', 'wizard_id', u'Invoice Lines')

    def contract_line(self, line, active_id):
        return {'analytic_account_id': active_id,
                'product_id': line.product_id.id,
                'uom_id': line.product_id.uom_id.id,
                'name': line.description,
                'quantity': line.quantity,
                'discount': line.discount,
                'price_unit': line.price_unit,
                }

    @api.multi
    def update_contract(self):
        active_ids = self._context.get('active_ids', [])
        analytic_inv_line = self.env['account.analytic.invoice.line']
        for active_id in active_ids:
            for line in self.invoice_lines:
                vals = self.contract_line(line, active_id)
                analytic_inv_line.create(vals)
        return True


class UpdateInvoiceLineWizardLine(models.TransientModel):
    _name = 'update.invoice.line.wizard.line'

    quantity = fields.Float(u'Quantity')
    price_unit = fields.Float(u'Unit Price')
    discount = fields.Float(u'Discount')
    product_id = fields.Many2one('product.product', u'Product')
    description = fields.Text(u'Description')
    wizard_id = fields.Many2one('update.invoice.line.wizard', u'Wizard')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price
            self.description  = self.product_id.name
