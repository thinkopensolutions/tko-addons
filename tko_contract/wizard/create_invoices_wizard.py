# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class CreateInvoicesWizard(models.TransientModel):
    _name = 'create.invoices.wizard'

    # Create Mass Invoices
    @api.multi
    def create_invoices(self):
        active_ids = self._context.get('active_ids', [])
        return self.env['account.analytic.account'].browse(active_ids).recurring_create_invoice()
