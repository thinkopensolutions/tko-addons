# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _


class UpdateInvoiceLineWizard(models.TransientModel):
    _inherit = 'update.invoice.line.wizard'

    def contract_line(self, line, active_id):
        result = super(UpdateInvoiceLineWizard, self).contract_line(line, active_id)
        result.update({
            'cost_center_id': line.cost_center_id.id,
            'account_analytic_id': line.account_analytic_id.id,
            'analytics_id': line.analytics_id.id,
            'start_date': line.start_date,
            'end_date': line.end_date
            ,
        })
        return result


class UpdateInvoiceLineWizardLine(models.TransientModel):
    _inherit = 'update.invoice.line.wizard.line'

    cost_center_id = fields.Many2one('account.cost.center', u'Centro de Custo')
    account_analytic_id = fields.Many2one('account.analytic.account', u'Conta Analitica')
    analytics_id = fields.Many2one('account.analytic.plan.instance', u'Conta Distribution')
    start_date = fields.Date(u'Start Date')
    end_date = fields.Date(u'End Date')

    @api.onchange('account_analytic_id', 'analytics_id')
    def onchange_analytic_account(self):
        if self.account_analytic_id:
            self.analytics_id = False
        if self.analytics_id:
            self.account_analytic_id = False
