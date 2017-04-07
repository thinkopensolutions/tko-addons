from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_discount += (line.product_uom_qty * line.price_unit * line.discount)/100
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_discount': order.pricelist_id.currency_id.round(amount_discount),
                'amount_total': amount_untaxed + amount_tax,
            })

    discount_type = fields.Selection([ ('fi', 'Fixed'), ('p', 'Percentage')], string='Discount type',
                                     readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='p')
    discount_rate = fields.Float('Discount Rate', digits_compute=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
                                 track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   track_visibility='always')
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all',
                                      digits_compute=dp.get_precision('Account'), track_visibility='always')

    @api.onchange('discount_type', 'discount_rate')
    def supply_rate(self):
        for order in self:
            total =0.0
            for line in order.order_line:
                total += round((line.product_uom_qty * line.price_unit))
            order.amount_discount =(order.discount_rate * total) / 100
            if order.discount_type == 'p':
                for line in order.order_line:
                    line.discount = order.discount_rate
            else:
                discount = 0.0
                if order.discount_rate != 0 and total != 0:
                    discount = (order.discount_rate * 100) / total
                for line in order.order_line:
                    line.discount = discount

    # @api.multi
    # def _prepare_invoice(self):
    #     invoice_vals = super(SaleOrder, self)._prepare_invoice()
    #     invoice_vals.update({
    #         'discount_type': self.discount_type,
    #         'discount_rate': self.discount_rate
    #     })
    #     return invoice_vals