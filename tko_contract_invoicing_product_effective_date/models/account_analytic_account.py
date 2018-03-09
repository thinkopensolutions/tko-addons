# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning

class AccountAnalyticAccont(models.Model):
    _inherit = 'account.analytic.account'

    end_date = fields.Date(u'End Date')

    api.multi

    def _create_invoice(self):
        dates = self.recurring_invoice_line_ids.mapped('start_date')
        unique_invoices = {}
        for line in self.recurring_invoice_line_ids:
            if line.start_date in unique_invoices.keys():
                unique_invoices[line.start_date].append(line)
            else:
                unique_invoices[line.start_date] = [line]


        self.ensure_one()
        # create separate invoice for each separate group of date
        for key,vals in unique_invoices.iteritems():
            invoice_vals = self._prepare_invoice()
            invoice = self.env['account.invoice'].create(invoice_vals)
            invoice.write({'date_invoice': key})
            # create invoice lines
            for line in vals:
                invoice_line_vals = self._prepare_invoice_line(line, invoice.id)
                self.env['account.invoice.line'].create(invoice_line_vals)

            invoice.compute_taxes()
        return invoice

    @api.multi
    def recurring_create_invoice(self):
        for contract in self:
            old_date = fields.Date.from_string(
                contract.recurring_next_date or fields.Date.today())
            new_date = old_date + self.get_relative_delta(
                contract.recurring_rule_type, contract.recurring_interval)
            ctx = self.env.context.copy()
            ctx.update({
                'old_date': old_date,
                'next_date': new_date,
                # Force company for correct evaluate domain access rules
                'force_company': contract.company_id.id,
            })
            # Re-read contract with correct company
            contract.with_context(ctx)._create_invoice()
            contract.write({
                'recurring_next_date': new_date.strftime('%Y-%m-%d')
            })
        return True


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    start_date = fields.Date(u'Start Date')
    end_date = fields.Date(u'End Date')

    @api.multi
    @api.constrains('start_date','end_date')
    def validate_start_end_date(self):
        for record in self:
            if record.start_date < record.analytic_account_id.date_start:
                raise Warning("Start date must be greater than %s" %record.analytic_account_id.date_start)
            if record.end_date > record.analytic_account_id.end_date:
                raise Warning("End date must be less than %s" %record.analytic_account_id.end_date)