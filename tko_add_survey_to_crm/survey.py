# -*- encoding: utf-8 -*-

from openerp import models, fields, api
class survey_user_input(models.Model):
    ''' Metadata for a set of one user's answers to a particular survey '''
    _name = "survey.user_input"
    _inherit = "survey.user_input"

    lead_id = fields.Many2one('crm.lead', string="About Lead:")

    @api.model
    def create(self, vals):
        context = self.env.context
        if context.get('active_model') == 'crm.lead' and context.get('active_id', False):
            vals.update({'lead_id' : context.get('active_id')})
        return super(survey_user_input, self).create(vals)

    @api.multi
    def write(self, vals):
        return super(survey_user_input, self).write(vals)