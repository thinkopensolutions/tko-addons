# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _

class UpdateInvoiceLineWizard(models.TransientModel):
    _name = 'update.invoice.line.wizard'

    invoice_lines = fields.One2many('update.invoice.line.wizard.line','wizard_id',u'Invoice Lines')

    @api.multi
    def update_contract(self):
        active_ids = self._context.get('active_ids' , [])
        analytic_inv_line = self.env['account.analytic.invoice.line']
        for active_id in active_ids:
            for line in self.invoice_lines:
                analytic_inv_line.create({'analytic_account_id' : active_id ,
                                          'product_id' : line.product_id.id,
                                          'name' : line.product_id.name,
                                          'quantity' : line.quantity,
                                          'discount' : line.discount,
                                          })
        return True

class UpdateInvoiceLineWizardLine(models.TransientModel):
    _name  = 'update.invoice.line.wizard.line'

    quantity = fields.Float(u'Quantity')
    price_unit = fields.Float(u'Unit Price')
    discount = fields.Float(u'Discount')
    product_id = fields.Many2one('product.product',u'Product')
    wizard_id = fields.Many2one('update.invoice.line.wizard',u'Wizard')