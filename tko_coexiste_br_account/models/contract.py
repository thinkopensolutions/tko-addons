# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    partner_id = fields.Many2one('res.partner', related='analytic_account_id.partner_id',
                                 string='Cliente', store=True)
    code = fields.Char(related='analytic_account_id.code', string=u'Referência', store=True)
    cost_center_id = fields.Many2one('account.cost.center', string=u'Centro de Custo')
    account_analytic_id = fields.Many2one('account.analytic.account', string=u'Conta Analítica')
    analytics_id = fields.Many2one('account.analytic.plan.instance', string=u'Analytic Distribution')

    @api.onchange('account_analytic_id')
    def onchange_account_analytic_id(self):
        if self.account_analytic_id:
            self.analytics_id = False

    @api.onchange('analytics_id')
    def onchange_analytics_id(self):
        if self.analytics_id:
            self.account_analytic_id = False


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    expense_type_id = fields.Many2one('account.expense.type', string=u'Tipo de Despesa')
    payment_mode_id = fields.Many2one('payment.mode', string=u'Modo de pagamento')

    # create invoices with setting Payment Mode and Expense Type

    @api.multi
    def _create_invoice(self):
        self.ensure_one()
        invoice = super(AccountAnalyticAccount, self)._create_invoice()
        invoice.write({'expense_type_id': self.expense_type_id.id,
                       'payment_mode_id': self.payment_mode_id.id})
        return invoice

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        res = super(AccountAnalyticAccount, self)._prepare_invoice_line(line, invoice_id)

        # create default plan
        alines = []
        if line.account_analytic_id or line.analytics_id:
            res.update({'analytic_distribution': True})
        if line.account_analytic_id:
            aline = self.env['account.analytic.plan.invoice.line'].create(
                {'analytic_account_id': line.account_analytic_id.id,
                 'rate': 100})
            alines.append(aline.id)

        else:
            for dline in line.analytics_id.account_ids:
                aline = self.env['account.analytic.plan.invoice.line'].create(
                    {'analytic_account_id': dline.analytic_account_id.id,
                     'rate': dline.rate})
                alines.append(aline.id)
        res.update({'account_ids': [(6, 0, alines)], 'cost_center_id': line.cost_center_id.id or False})

        return res

    @api.multi
    def name_get(self):
        res = []
        for account in self:
            names = []
            current = account
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((account.id, account.name))
        return res
