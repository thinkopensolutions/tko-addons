# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cashflow_value = fields.Monetary(compute='_compute_value',
                                     name='Cashflow Value',
                                     store=True, readonly=True,
                                     currency_field='company_currency_id',
                                     help="The cash flow value is as defined "
                                          "in user account type.")
    cashflow_value_cash = fields.Monetary(compute='_compute_value',
                                     name='Cashflow Cash',
                                     store=True, readonly=True,
                                     currency_field='company_currency_id',
                                     help="The cash flow value is as defined "
                                          "in user account type.")

    @api.depends('debit', 'credit', 'balance',
                 'account_id.user_type_id.cashflow')
    def _compute_value(self):
        for record in self:
            if record.account_id.user_type_id.cashflow:
                if record.account_id.user_type_id.cashflow == 'none':
                    record.cashflow_value = 0
                elif record.account_id.user_type_id.cashflow == 'credit':
                    record.cashflow_value = \
                        getattr(record,
                                record.account_id.user_type_id.cashflow) * -1
                elif record.account_id.user_type_id.cashflow in ('debit',
                                                                 'balance'):
                    record.cashflow_value = \
                        getattr(record,
                                record.account_id.user_type_id.cashflow)
