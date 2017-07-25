# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
import datetime

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    partner_id = fields.Many2one('res.partner', string=u'Client', compute='get_partner')
    date_maturity = fields.Date(u'Due Date', compute='get_partner')


    @api.one
    def get_partner(self):
        model = self.res_model
        res_id = self.res_id
        if model and res_id:
            try:
                self.partner_id = self.env[model].browse(res_id).partner_id.id
            except:
                self.partner_id = False
            if model == 'account.invoice':
                self.date_maturity = self.env[model].browse(res_id).date_due