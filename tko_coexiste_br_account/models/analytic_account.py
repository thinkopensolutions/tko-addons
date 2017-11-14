# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _


class AccountAnalyticPayment(models.Model):
    _name = 'account.analytic.payment'
    _description = 'Analytic Payment Details'

    payment_date = fields.Date(string='Payment Date', required=True, copy=False)
    amount = fields.Float('Amount', copy=False)
    name = fields.Char('Name', copy=False)
    analytic_line_id = fields.Many2one('account.analytic.line', string='Analytic Line ID', copy=False)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    @api.depends('payment_move_line_ids')
    def _total_compute(self):
        for analytic_line in self:
            line_total = 0
            for line in analytic_line.payment_move_line_ids:
                line_total = line_total+line.amount
            analytic_line.line_total = line_total


    partner_id = fields.Many2one('res.partner', related='move_id.partner_id', string='Partner', store=True)
    company_id = fields.Many2one(related='move_id.company_id', string='Company', store=True, readonly=False)
    journal_id = fields.Many2one(related='move_id.journal_id', string='Journal', store=True, readonly=False)
    invoice_id = fields.Many2one('account.invoice', string='Invoice ID', copy=False)
    state = fields.Selection(related='invoice_id.state', string='State')
    date_due =fields.Date(related='invoice_id.date_due', string='Due Date')
    payment_line = fields.One2many(related='invoice_id.payment_line', string="Analytic Payment Lines")
    payment_move_line_ids = fields.Many2many(related='invoice_id.payment_move_line_ids', string="Analytic Payment Lines")
    line_total = fields.Float('Total', compute=_total_compute, store=True)

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
                # print"invoice>",invoice
                analytic_line_id.write({'invoice_id':invoice.id,'state':invoice.state, 'date_due':invoice.date_due})
                analytic_payment_vals = {
                    # 'payment_date':analytic_line_id.date,
                    'amount':analytic_line_id.amount,
                    'name':analytic_line_id,
                    'analytic_line_id':analytic_line_id.id
                }
                self.env['account.analytic.payment'].create(analytic_payment_vals)
                pass
        return True

    @api.multi
    def get_inv_history(self):
        payment_obj = self.env['account.payment']
        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        analytic_line_obj = self.env['account.analytic.line']
        analytic_lines = analytic_line_obj.search([])
        analytic_lines = set(analytic_lines)
        for line in analytic_lines:
            invoice = inv_obj.search([('move_id','=', line.move_id.move_id.id)])
            line.write({'invoice_id':invoice.id,'state':invoice.state, 'date_due':invoice.date_due})
            pass
        return True
