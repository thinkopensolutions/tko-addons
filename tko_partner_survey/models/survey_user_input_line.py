# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'

    partner_id = fields.Many2one(related='user_input_id.partner_id',
                                 store=True)
