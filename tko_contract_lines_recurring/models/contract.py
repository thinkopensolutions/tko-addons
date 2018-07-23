# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.depends('recurring_next_date', 'date_end', 'recurring_invoices')
    def _compute_create_invoice_visibility(self):
        for contract in self:
            contract.create_invoice_visibility = contract.recurring_invoices

    @api.constrains('date_start', 'date_end')
    def validate_invoice_line(self):
        for line in self.recurring_invoice_line_ids:
            print("contract : %s : %s" % (self.date_start, self.date_end))
            print("line : %s : %s" % (line.date_start, line.date_end))
            if line.date_start and line.date_end:
                if line.date_start < self.date_start or line.date_end > self.date_end:
                    raise ValidationError("%s must fall between %s - %s" % (
                        line.product_id.name, self.date_start , self.date_end))
        return True


    def check_expiry_lines(self):
        for line in self.recurring_invoice_line_ids:
            if line.date_end < fields.Date.today():
                line.state = 'i'
            return True

    @api.multi
    def recurring_create_invoice(self):
        """Create invoices from contracts

        :return: invoices created
        """
        self.check_expiry_lines()
        invoices = self.env['account.invoice']
        invoices_dict = {}
        for line in self.recurring_invoice_line_ids:
            if line.state == 'a':
                if line.recurring_next_date not in invoices_dict.keys():
                    invoices_dict[line.recurring_next_date] = [line]
                else:
                    invoices_dict[line.recurring_next_date].append(line)
        print (invoices_dict)
        ## update next recurring date on lines
        for line in self.recurring_invoice_line_ids:
            # compute from  today's date if not next date is not set
            old_date = fields.Date.from_string(line.recurring_next_date or fields.Date.today())
            new_date = old_date + self.get_relative_delta(
                line.recurring_rule_type, line.recurring_interval)

            # if line.state == 'a':
            #     line.recurring_next_date = new_date
        for key, value in invoices_dict.items():
            # prepare invoice without invoice line and update date from last next recurring date
            invoice = self.env['account.invoice'].create(
                self._prepare_invoice())
            invoice.date_invoice = key
            invoices |= invoice
            # set lines
            for line in value:
                print("line..............",line)
                invoice_line_vals = self._prepare_invoice_line(line, invoice.id)
                if invoice_line_vals:
                    self.env['account.invoice.line'].create(invoice_line_vals)
            invoices.compute_taxes()

        return True

        invoices = self.env['account.invoice']
        for contract in self:
            ref_date = contract.recurring_next_date or fields.Date.today()
            if (contract.date_start > ref_date or
                    contract.date_end and contract.date_end < ref_date):
                if self.env.context.get('cron'):
                    continue  # Don't fail on cron jobs
                raise ValidationError(
                    _("You must review start and end dates!\n%s") %
                    contract.name
                )
            old_date = fields.Date.from_string(ref_date)
            new_date = old_date + self.get_relative_delta(
                contract.recurring_rule_type, contract.recurring_interval)
            ctx = self.env.context.copy()
            ctx.update({
                'old_date': old_date,
                'next_date': new_date,
                # Force company for correct evaluation of domain access rules
                'force_company': contract.company_id.id,
            })
            # Re-read contract with correct company
            invoices |= contract.with_context(ctx)._create_invoice()
            contract.write({
                'recurring_next_date': fields.Date.to_string(new_date)
            })
        return invoices


class AccountAnalyticAccountLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    state = fields.Selection([('a', 'Active'), ('i', 'Inactive')], string=u'State', default='a', copy=False)
    date_start = fields.Date('Date Start', default=fields.Date.context_today, copy=False)
    date_end = fields.Date('Date End', copy=False)
    recurring_next_date = fields.Date('Date of Next Invoice', default=fields.Date.context_today,
                                      copy=False, )
    recurring_interval = fields.Integer(
        default=1,
        string='Repeat Every',
        help="Repeat every (Days/Week/Month/Year)",
    )
    recurring_rule_type = fields.Selection(
        [('daily', 'Day(s)'),
         ('weekly', 'Week(s)'),
         ('monthly', 'Month(s)'),
         ('monthlylastday', 'Month(s) last day'),
         ('yearly', 'Year(s)'),
         ],
        default='monthly',
        string='Recurrence',
        help="Specify Interval for automatic invoice generation.",
    )

    @api.constrains('date_start', 'date_end')
    def validate_invoice_line(self):
        contract_date_start = self.analytic_account_id.date_start
        contract_date_end = self.analytic_account_id.date_end
        if self.date_start and self.date_end:
            if self.date_start < contract_date_start or self.date_end > contract_date_end:
                raise ValidationError("%s must fall between %s - %s" % (
                    self.product_id.name, contract_date_start, contract_date_end))
        return True
