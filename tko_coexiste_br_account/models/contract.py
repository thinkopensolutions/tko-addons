# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    expense_type_id = fields.Many2one('account.expense.type', string=u'Tipo de Despesa')
    payment_mode_id = fields.Many2one('payment.mode', string=u'Modo de pagamento')

    # create invoices with setting Payment Mode and Expense Type

    @api.multi
    def _create_invoice(self):
        self.ensure_one()
        invoice = super(AccountAnalyticAccount, self)._create_invoice()
        invoice.write({'expense_type_id' : self.expense_type_id.id,
                       'payment_mode_id': self.payment_mode_id.id})
        return invoice
