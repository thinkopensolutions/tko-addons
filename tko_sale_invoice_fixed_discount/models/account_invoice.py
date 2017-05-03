from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        self.amount_discount = sum((line.quantity * line.price_unit * line.discount)/100 for line in self.invoice_line_ids)
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    discount_type = fields.Selection([('fi', 'Fixed'), ('p', 'Percentage')], string='Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='p')
    discount_rate = fields.Float('Discount Amount', digits=(16, 2), readonly=True, states={'draft': [('readonly', False)]})
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_compute_amount',
                                      track_visibility='always')

    @api.onchange('discount_type', 'discount_rate', 'invoice_line_ids')
    def supply_rate(self):
        for inv in self:
            total = 0.0
            for line in inv.invoice_line_ids:
                total += round((line.quantity * line.price_unit))
            if inv.discount_type == 'p':
                for line in inv.invoice_line_ids:
                    line.discount = inv.discount_rate
            else:
                discount = 0.0
                if inv.discount_rate != 0 and total !=0:
                    discount = (inv.discount_rate * 100) / total
                for line in inv.invoice_line_ids:
                    line.discount = discount

    @api.multi
    def button_dummy(self):
        self.supply_rate()
        return True

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        #Calculate a discount when it is fixed and set on line as a percentage
        if res.discount_type == 'fi':
            self.add_fixed_amount_percentage(res)
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        #Calculate a discount when it is fixed and set on line as a percentage
        if self.discount_type == 'fi':
            self.add_fixed_amount_percentage(self)
        return res

    @api.multi
    def add_fixed_amount_percentage(self,res):
        total = 0.0
        for line in res.invoice_line_ids:
            total += round((line.quantity * line.price_unit))
        if total:
            discount = (res.discount_rate *100)/ total
            for line in res.invoice_line_ids:
                line.write({'discount':discount})

    @api.onchange('discount_type')
    def onchange_discount_type(self):
        self.discount_rate = 0

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)

    @api.onchange('quantity','price_unit')
    def onchange_discount(self):
        if self.invoice_id:
            if self.invoice_id.discount_type == 'p':
                self.discount = self.invoice_id.discount_rate
