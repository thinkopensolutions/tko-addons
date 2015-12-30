from openerp import fields, models, api, _

class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    discount_on_order  = fields.Float(string='Discount on Order')
    
    
    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount', 'discount_on_order')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.amount_tax = sum(line.amount for line in self.tax_line)
        self.amount_total = self.amount_untaxed + self.amount_tax - self.discount_on_order