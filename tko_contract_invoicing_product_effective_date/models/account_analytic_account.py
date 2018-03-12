# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

class AccountAnalyticAccont(models.Model):
    _inherit = 'account.analytic.account'

    end_date = fields.Date(u'End Date')

    def _validate_invoice_creating(self):
        for line in self.recurring_invoice_line_ids:
            if line.start_date <= self.recurring_next_date and line.end_date >=self.recurring_next_date:
                return True
        return False

    # Add invoce lines only Contract's Date of Next Invoice
    # falls in the range of start and end date of line
    @api.multi
    def _create_invoice(self):
        if self._validate_invoice_creating():
            self.ensure_one()
            invoice_vals = self._prepare_invoice()
            invoice = self.env['account.invoice'].create(invoice_vals)
            for line in self.recurring_invoice_line_ids:
                if line.start_date <= self.recurring_next_date and line.end_date >= self.recurring_next_date:
                    invoice_line_vals = self._prepare_invoice_line(line, invoice.id)
                    self.env['account.invoice.line'].create(invoice_line_vals)
            invoice.compute_taxes()
            return invoice
        else:
            _logger.warn(u"No Invoice to be created for date %s" %self.recurring_next_date)
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