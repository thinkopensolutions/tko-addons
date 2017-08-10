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
                analytic_line_id = self.env['account.analytic.line'].search([('invoice_id','=',invoice.id)]) 
                analytic_payment_vals = {
                    'payment_date':vals.get('payment_date'),
                    'amount':vals.get('amount'),
                    'name':res,
                    'analytic_line_id':analytic_line_id.id
                }
                self.env['account.analytic.payment'].create(analytic_payment_vals)
        return res


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    partner_id = fields.Many2one('res.partner', related='move_id.partner_id', string='Partner', store=True)
    company_id = fields.Many2one(related='move_id.company_id', string='Company', store=True, readonly=False)
    journal_id = fields.Many2one(related='move_id.journal_id', string='Journal', store=True, readonly=False)
    invoice_id = fields.Many2one('account.invoice', string='Invoice ID', copy=False)
    state = fields.Selection(related='invoice_id.state', string='State')
    date_due =fields.Date(related='invoice_id.date_due', string='Due Date')
    payment_line = fields.One2many('account.analytic.payment', 'analytic_line_id', string="Analytic Payment Lines")

    @api.model
    def create(self, vals):
        context = self.env.context
        if vals.get('move_id'):
            move_id = self.env['account.move.line'].browse(vals.get('move_id'))
            invoice = move_id.invoice_id.id
            vals.update({'invoice_id': invoice})
        return super(AccountAnalyticLine, self).create(vals)


