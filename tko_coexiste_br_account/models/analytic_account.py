# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _


class AccountAnalyticPayment(models.Model):
    _name = 'account.analytic.payment'
    _description = 'Analytic Payment Details'

    payment_date = fields.Date(string='Payment Date', required=True, copy=False)
    amount = fields.Float('Amount', copy=False)
    name = fields.Char('Name', copy=False)
    analytic_line_id = fields.Many2one('account.analytic.line', string='Analytic Line ID', copy=False)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def create(self, vals):
        res = super(AccountPayment, self).create(vals)
        if vals.get('communication'):
            invoice = self.env['account.invoice'].search([('number','=', vals.get('communication'))])
            if invoice:
                remain = 0
                analytic_line_ids = self.env['account.analytic.line'].search([('invoice_id','=',invoice.id)]) 
                analytic_line_ids = [x for x in analytic_line_ids if (x.amount != x.line_total)]
                remain = vals.get('amount') 
                total = 0
                for analytic_line_id in analytic_line_ids:
                    if analytic_line_id.line_total == analytic_line_id.amount:
                        pass
                    if remain >= analytic_line_id.amount and remain >= analytic_line_id.line_total:
                        pay_amount = analytic_line_id.amount-analytic_line_id.line_total
                        analytic_payment_vals = {
                            'payment_date':vals.get('payment_date'),
                            'amount':pay_amount,
                            'name':res,
                            'analytic_line_id':analytic_line_id.id
                        }
                        total = total + pay_amount
                        line_id = self.env['account.analytic.payment'].create(analytic_payment_vals)
                        remain = vals.get('amount') - total
                    # elif remain < analytic_line_id.amount and remain >= analytic_line_id.line_total:
                    #     plan_total = remain + analytic_line_id.line_total
                    #     if analytic_line_id.amount <= plan_total:
                    #         pay_amount = remain
                    #     else:
                    #         pay_amount = analytic_line_id.amount - analytic_line_id.line_total
                    else:
                        if remain > 0:
                            if remain < analytic_line_id.amount and remain <= analytic_line_id.line_total:
                                pay_amount = remain
                            else:
                                pay_amount = analytic_line_id.amount-analytic_line_id.line_total
                                if pay_amount >= remain:
                                    pay_amount = remain
                                else:
                                    pay_amount = remain - pay_amount
                            analytic_payment_vals = {
                                'payment_date':vals.get('payment_date'),
                                'amount':pay_amount,
                                'name':res,
                                'analytic_line_id':analytic_line_id.id
                            }
                            total = total + pay_amount
                            line_id = self.env['account.analytic.payment'].create(analytic_payment_vals)
                            remain = vals.get('amount') - total
        return res



class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'


    @api.multi
    @api.depends('payment_line')
    def _total_compute(self):
        for analytic_line in self:
            line_total = 0
            for line in analytic_line.payment_line:
                line_total = line_total+line.amount
            analytic_line.line_total = line_total

    partner_id = fields.Many2one('res.partner', related='move_id.partner_id', string='Partner', store=True)
    company_id = fields.Many2one(related='move_id.company_id', string='Company', store=True, readonly=False)
    journal_id = fields.Many2one(related='move_id.journal_id', string='Journal', store=True, readonly=False)
    invoice_id = fields.Many2one('account.invoice', string='Invoice ID', copy=False)
    state = fields.Selection(related='invoice_id.state', string='State')
    date_due =fields.Date(related='invoice_id.date_due', string='Due Date')
    company_id = fields.Many2one(related='move_id.company_id', string='Company', store=True, readonly=False)
    journal_id = fields.Many2one(related='move_id.journal_id', string='Journal', store=True, readonly=False)
    invoice_id = fields.Many2one('account.invoice', string='Invoice ID', copy=False)
    state = fields.Selection(related='invoice_id.state', string='State')
    date_due =fields.Date(related='invoice_id.date_due', string='Due Date')
    payment_line = fields.One2many(related='invoice_id.payment_line', string="Analytic Payment Lines")
    line_total = fields.Float('Total', compute='_total_compute', store=True)

    @api.model
    def create(self, vals):
        context = self.env.context
        if vals.get('move_id'):
            move_id = self.env['account.move.line'].browse(vals.get('move_id'))
            invoice = move_id.invoice_id.id
            vals.update({'invoice_id': invoice})
        return super(AccountAnalyticLine, self).create(vals)

    @api.multi
    def get_history(self):
        payment_obj = self.env['account.payment']
        inv_line_obj = self.env['account.invoice.line']
        analytic_line_obj = self.env['account.analytic.line']
        inv_lines = inv_line_obj.search([('account_analytic_id','!=', False)])
        invoices = [x.invoice_id for x in inv_lines if x.invoice_id.state == 'paid']
        invoices = set(invoices)
        for invoice in invoices:
            paymnets = payment_obj.search([('communication','=', invoice.number)])
            move_lines = [x.id for x in invoice.move_id.line_ids]
            analytic_lines = analytic_line_obj.search([('move_id','in', move_lines)])
            for analytic_line_id in analytic_lines:
                analytic_payment_vals = {
                    'payment_date':analytic_line_id.date,
                    'amount':analytic_line_id.amount,
                    'name':analytic_line_id,
                    'analytic_line_id':analytic_line_id.id
                }
                self.env['account.analytic.payment'].create(analytic_payment_vals)
                pass
        return True