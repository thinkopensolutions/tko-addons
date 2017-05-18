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
from openerp import models, fields, api
from openerp.exceptions import Warning


class account_voucher(models.Model):
    _inherit = 'account.voucher'

    move_line_id = fields.Many2one('account.move.line', 'Installment')
    domain_move_lines = fields.Many2many('account.move.line', compute='_get_domain_move_lines', string='Move Lines')

    @api.model
    def default_get(self, fields_list):
        data = super(account_voucher, self).default_get(fields_list)
        inv_id = self.env.context.get('active_id', False)
        if inv_id:
            data['domain_move_lines'] = [(6, 0, [mline.id for mline in
                                                 self.env['account.invoice'].browse(inv_id).move_line_receivable_id if
                                                 mline.remaining_amount])]
        return data

    @api.multi
    def _get_domain_move_lines(self):
        inv_id = self.env.context.get('active_id', False)
        if inv_id:
            self.domain_move_lines = [(6, 0, [mline.id for mline in
                                              self.env['account.invoice'].browse(inv_id).move_line_receivable_id if
                                              mline.remaining_amount])]

    @api.onchange('move_line_id')
    def change_move_line_id(self):
        inv_id = self.env.context.get('active_id', False)
        if not self.move_line_id:
            self.amount = 0.0
        else:
            self.amount = self.move_line_id.remaining_amount

    @api.multi
    def post(self):
        context = context or {}
        for voucher in self:
            if voucher.amount > voucher.move_line_id.remaining_amount:
                raise Warning('Maximum amount to be paid is %s' % voucher.move_line_id.remaining_amount)
        return super(account_voucher, self).post()

    @api.onchange('line_ids','amount', 'currency_id')
    # def onchange_line_ids(self, cr, uid, ids, line_dr_ids, line_cr_ids, amount, voucher_currency, type, context=None):
    def onchange_line_ids(self):
        # context = context or {}
        if not self.line_ids :#and not self.line_cr_ids:
            return {'value': {'writeoff_amount': 0.0}}
        # resolve lists of commands into lists of dicts
        # self.line_ids = self.resolve_2many_commands('line_ids', self.line_ids, ['amount'])
        # self.line_cr_ids = self.resolve_2many_commands('line_cr_ids', self.line_cr_ids, ['amount'])
        # set correct move_id in line
        move_line_id = self._context.get('move_line_id', False)
        for line in line_cr_ids[1:]:
            if line['move_line_id'] == move_line_id:
                line['amount'] = amount
            else:
                line['amount'] = 0.0

        # compute the field is_multi_currency that is used to hide/display options linked to secondary currency on the voucher
        is_multi_currency = False
        # loop on the voucher lines to see if one of these has a secondary currency. If yes, we need to see the options
        for voucher_line in self.line_ids:# + line_cr_ids:
            line_id = voucher_line.get('id') and self.env['account.voucher.line'].browse(voucher_line['id']).move_line_id.id or voucher_line.get('move_line_id')
            if line_id and self.env['account.move.line'].browse(line_id).currency_id:
                is_multi_currency = True
                break
                # self._compute_writeoff_amount(self.line_dr_ids, line_cr_ids, amount, type),
        return {
            'value': {'writeoff_amount': self._compute_writeoff_amount(self.line_ids, amount, type),
                      'is_multi_currency': is_multi_currency,
                      'line_cr_ids': line_cr_ids,
                      }}


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    remaining_amount = fields.Float(string='Remaining Amount', compute='get_move_line_amount')
    paid_amount = fields.Float(string='Paid Amount', compute='get_move_line_amount')

    @api.multi
    def name_get(self):
        if not self._ids:
            return []
        result = []
        for line in self:
            result.append((line.id, line.name))
        return result

    @api.depends('paid_amount')
    def get_move_line_amount(self):
        for record in self:
            # customer invoices
            if record.invoice_id.type == 'out_invoice':
                if record.full_reconcile_id:
                    debit = 0.0
                    credit = 0.0
                    for line in record.full_reconcile_id.reconciled_line_ids:
                        debit += line.debit
                        credit += line.credit
                    record.remaining_amount = debit - credit
                    record.paid_amount = credit
                # elif record.reconcile_id:
                #     record.remaining_amount = 0.0
                #     record.paid_amount = record.debit
                else:
                    record.remaining_amount = record.debit
                    record.paid_amount = 0.0
            # supplier invoices
            if record.invoice_id.type == 'in_invoice':
                if record.full_reconcile_id:
                    debit = 0.0
                    credit = 0.0
                    for line in record.full_reconcile_id.reconciled_line_ids:
                        debit += line.debit
                        credit += line.credit
                    record.remaining_amount = credit - debit
                    record.paid_amount = debit
                # elif record.reconcile_id:
                #     record.remaining_amount = 0.0
                #     record.paid_amount = record.credit
                else:
                    record.remaining_amount = record.credit
                    record.paid_amount = 0.0


class AccountFullReconcile(models.Model):
    _inherit = "account.full.reconcile"
    _description = "Account Reconciliation"

    remaining_amount = fields.Float(string='Remaining Amount', compute='get_remaining_amount')

    @api.multi
    @api.depends('reconciled_line_ids')
    def get_remaining_amount(self):
        for record in self:
            print "reduce(lambda y,t: (t.debit or 0.0) - (t.credit or 0.0) + y, record.reconciled_line_ids, 0.0)............", reduce(
                lambda y, t: (t.debit or 0.0) - (t.credit or 0.0) + y, record.reconciled_line_ids, 0.0)
            total = reduce(lambda y, t: (t.debit or 0.0) - (t.credit or 0.0) + y, record.reconciled_line_ids, 0.0)

            record.remaining_amount = total