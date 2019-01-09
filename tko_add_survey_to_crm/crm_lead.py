# -*- coding: utf-8 -*-

from openerp import models, osv, fields, api, _
import logging

class crm_stage(models.Model):
    _inherit = "crm.stage"

    template_id = fields.Many2one('mail.template', string="Template")
