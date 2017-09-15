# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import json
from openerp import models, fields, api, _
import datetime
from odoo.exceptions import Warning as UserError
from odoo.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from odoo.tools import float_is_zero, float_compare


class AccountExpenseType(models.Model):
    _name = 'account.expense.type'

    name = fields.Char('Name')
    expense_type = fields.Selection([('c', 'Customer Inovice'), ('s', 'Supplier Invoice'), ('b', 'Both')],
                                    required=True, default='b', string='InvoiceType')


class AccountMove(models.Model):
    _inherit = 'account.move'

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('date_maturity')
    def onchange_date_maturity(self):
        partner = self.partner_id
        move_line_ids = self.search([('move_id','=',self.move_id.id)])
        account_ids = []
        account_ids.append(partner.property_account_receivable_id.id)
        account_ids.append(partner.property_account_payable_id.id)
        if self.account_id.id in account_ids:
            date_maturity = self.date_maturity
            for line in move_line_ids:
                line.write({'date_maturity': date_maturity})

    @api.model
    def create(self, vals):
        if vals.get('invoice_id'):
            invoice = self.env['account.invoice'].search([('id','=',vals.get('invoice_id'))])
            vals.update({'date_maturity':invoice.date_due})
        return super(AccountMoveLine, self).create(vals)

    @api.multi
    def write(self, values):
        result = super(AccountMoveLine, self).write(values)
        if values.get('date_maturity'):
            context = self.env.context
            if context.get('pass_date_maturity'):
                return result
            for record in self:
                partner = self.partner_id
                account_ids = []
                account_ids.append(partner.property_account_receivable_id.id)
                account_ids.append(partner.property_account_payable_id.id)
                move_line_ids = self.search([('move_id','=',self.move_id.id),('id','!=',self.id)])
                if self.account_id.id in account_ids:
                    date_maturity = values.get('date_maturity')
                    for line in move_line_ids:
                        ctx = {'pass_date_matury':True}
                        line.with_context(ctx).write({'date_maturity': date_maturity})
        return result


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def post(self):
        res = super(AccountPayment, self).post()
        for res in self:
            for invoice in res.invoice_ids:
                if invoice.type == 'out_invoice':
                    invoice.move_id.date = datetime.datetime.now()
                    invoice.move_id.state = 'posted'
                    # for move_line in invoice.move_id.line_ids:
                    #     if move_line.credit > 0:
                    #         move_line.date_maturity = invoice.move_id.date
        return res

    # @api.model
    # def create(self, vals):
    #     res = super(AccountPayment, self).create(vals)
    #     if vals.get('communication'):
    #         invoice = self.env['account.invoice'].search([('number','=', vals.get('communication'))])
    #         if invoice:
    #             invoice_payment_vals = {
    #                 'payment_date':vals.get('payment_date'),
    #                 'amount':vals.get('amount'),
    #                 'name':res,
    #                 'invoice_id':invoice.id,
    #                 # 'move_line_id':res.id,
    #             }
    #             self.env['invoice.payment.info'].create(invoice_payment_vals)
    #     return res


class InvoicePaymentInfo(models.Model):
    _name = 'invoice.payment.info'
    _description = 'Invoice Payment Details'

    payment_date = fields.Date(string='Payment Date', copy=False)
    name = fields.Char('Name', copy=False)
    invoice_id = fields.Many2one('account.invoice', string='Invoice ID', copy=False)
    move_line_id = fields.Many2one('account.move.line', string='Move Line', copy=False)
    currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id', readonly=True,
        help='Utility field to express amount currency')
    amount = fields.Monetary(string='Amount', copy=False, required=True, currency_field='currency_id')


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('payment_move_line_ids.amount_residual')
    def _get_payment_info_JSON(self):
        self.payments_widget = json.dumps(False)
        if self.payment_move_line_ids:
            info = {'title': _('Less Payment'), 'outstanding': False, 'content': []}
            currency_id = self.currency_id
            for payment in self.payment_move_line_ids:
                payment_currency_id = False
                if self.type in ('out_invoice', 'in_refund'):
                    amount = sum([p.amount for p in payment.matched_debit_ids if p.debit_move_id in self.move_id.line_ids])
                    amount_currency = sum([p.amount_currency for p in payment.matched_debit_ids if p.debit_move_id in self.move_id.line_ids])
                    if payment.matched_debit_ids:
                        payment_currency_id = all([p.currency_id == payment.matched_debit_ids[0].currency_id for p in payment.matched_debit_ids]) and payment.matched_debit_ids[0].currency_id or False
                elif self.type in ('in_invoice', 'out_refund'):
                    amount = sum([p.amount for p in payment.matched_credit_ids if p.credit_move_id in self.move_id.line_ids])
                    amount_currency = sum([p.amount_currency for p in payment.matched_credit_ids if p.credit_move_id in self.move_id.line_ids])
                    if payment.matched_credit_ids:
                        payment_currency_id = all([p.currency_id == payment.matched_credit_ids[0].currency_id for p in payment.matched_credit_ids]) and payment.matched_credit_ids[0].currency_id or False
                # get the payment value in invoice currency
                if payment_currency_id and payment_currency_id == self.currency_id:
                    amount_to_show = amount_currency
                else:
                    amount_to_show = payment.company_id.currency_id.with_context(date=payment.date).compute(amount, self.currency_id)
                if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                    continue
                payment_ref = payment.move_id.name
                if payment.move_id.ref:
                    payment_ref += ' (' + payment.move_id.ref + ')'
                info['content'].append({
                    'name': payment.name,
                    'journal_name': payment.journal_id.name,
                    'amount': amount_to_show,
                    'currency': currency_id.symbol,
                    'digits': [69, currency_id.decimal_places],
                    'position': currency_id.position,
                    'date': payment.date,
                    'payment_id': payment.id,
                    'move_id': payment.move_id.id,
                    'ref': payment_ref,
                })
                payment_info_obj = self.env['invoice.payment.info']
                pay_info_line = payment_info_obj.search([('move_line_id','=',payment.id),('invoice_id','=',self.id)])
                if not pay_info_line:
                    invoice_payment_vals = {
                        'payment_date':payment.date,
                        'amount':amount_to_show,
                        'name':payment.name,
                        'invoice_id':self.id,
                        'currency_id':currency_id.id,
                        'move_line_id': payment.id,
                    }
                    pay_info_id = self.env['invoice.payment.info'].create(invoice_payment_vals)
            self.payments_widget = json.dumps(info)


    expense_type_id = fields.Many2one('account.expense.type', string=u'Expense Type')
    payment_line = fields.One2many('invoice.payment.info', 'invoice_id', string="Invoice Payment Lines")
    payment_date = fields.Date(related='payment_line.payment_date', string='Payment Date')
    payments_widget = fields.Text(compute='_get_payment_info_JSON')
    # payment_move_line_ids = fields.Many2many('account.move.line', string='Payment Move Lines', compute='_compute_payments', store=True)

    # set move date
    @api.multi
    def action_invoice_paid(self):
        # lots of duplicate calls to action_invoice_paid, so we remove those already paid
        to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
        result = super(AccountInvoice, self).action_invoice_paid()
        for invoice in to_pay_invoices:
            if invoice.move_id:
                if invoice.type == 'out_invoice':
                    invoice.move_id.date = datetime.datetime.now()
                    invoice.move_id.state = 'posted'
                    # for move_line in invoice.move_id.line_ids:
                    #     if move_line.credit > 0:
                    #         move_line.date_maturity = invoice.move_id.date
        return result

    # set account Account Move to unposted
    def action_invoice_re_open(self):
        result = super(AccountInvoice, self).action_invoice_re_open()
        if self.type in ('out_invoice', 'out_refund'):
            self.move_id.write({'state': 'draft'})
        return result

    @api.model
    def create(self, vals):
        result = super(AccountInvoice, self).create(vals)
        # due_date = vals.get('date_due') or self.date_due
        # date = vals.get('date') or self.date
        # if due_date and date:
        #     due_date = datetime.datetime.strptime(due_date, OE_DFORMAT).date()
        #     date = datetime.datetime.strptime(date, OE_DFORMAT).date()
        #     if due_date < date:
        #         # raise ValidationError(
        #         # _("You can not set Due Date Less than Invoice date."))
        #         return False
        return result


    @api.multi
    def write(self, vals):
        due_date = vals.get('date_due') or self.date_due
        date = vals.get('date') or self.date
        if due_date and date:
            due_date = datetime.datetime.strptime(due_date, OE_DFORMAT).date()
            date = datetime.datetime.strptime(date, OE_DFORMAT).date()
            # if due_date < date:
            #     # raise ValidationError(
            #     # _("You can not set Due Date Less than Invoice date."))
            #     return False
            for move_line in self.move_id.line_ids:
                move_line.date_maturity = due_date
        return super(AccountInvoice, self).write(vals)

    @api.multi
    def update_history(self):
        payment_obj = self.env['account.payment']
        inv_obj = self.env['account.invoice']
        invoices = inv_obj.search([])
        invoices = set(invoices)
        for invoice in invoices:
            if invoice.payments_widget != u'false':
                info = json.loads(invoice.payments_widget)
                for content in info.get('content'):
                    for data in content:
                        if data == 'payment_id':
                            payment_id = content[data]
                            payment_id = payment_obj.search([('id','=',int(payment_id))])
                        if data == 'date':
                            payment_date = content[data]
                        if data == 'amount':
                            amount = content[data]
                        if data == 'name':
                            name = content[data]
                    invoice_payment_vals = {
                        'payment_date':payment_date,
                        'amount':amount,
                        'name':name,
                        'invoice_id':invoice.id,
                        'currency_id':payment_id.currency_id.id
                    }
                    self.env['invoice.payment.info'].create(invoice_payment_vals)
        return True

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    service_type_id = fields.Many2one(
        'br_account.service.type', related='product_id.service_type_id', string=u'Tipo de Serviço')
