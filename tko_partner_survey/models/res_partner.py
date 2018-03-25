# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api
from openerp.exceptions import Warning


class ResPartner(models.Model):
    _inherit = 'res.partner'

    survey_id = fields.Many2one('survey.survey', u'Survey')
    survey_input_lines = fields.One2many(
        comodel_name='survey.user_input_line', inverse_name='partner_id',
        string='Surveys answers')
    survey_inputs = fields.One2many(
        comodel_name='survey.user_input', inverse_name='partner_id',
        string='Surveys')
    survey_input_count = fields.Integer(
        string='Survey number', compute='_count_survey_input',
        store=True)

    @api.one
    @api.depends('survey_inputs')
    def _count_survey_input(self):
        self.survey_input_count = len(self.survey_inputs)


    @api.multi
    def send_partner_survey(self, survey_id):
        # Calling method from button sends context in survey_id
        # we check it to be integer value
        if not isinstance(survey_id, int):
            survey_id = False
        templates = self.env['ir.model.data'].get_object_reference('survey', 'email_template_survey')
        if len(templates):
            template_id = templates[1] if len(templates) > 0 else False
            for partner in self:
                if not partner.survey_id:
                    raise Warning("Survey not set in partner")
                composer = self.env['survey.mail.compose.message'].create({
                    'model': 'res.partner',
                    'res_id': partner.id,
                    'partner_ids': [(6, 0, [partner.id])],
                    'survey_id':  survey_id or partner.survey_id.id,
                    'template_id': template_id,
                    'composition_mode': 'comment'
                })
                # Get mail body on from onchange_template_id
                values = composer.onchange_template_id(template_id, 'comment', 'res.partner', partner.id)['value']
                # use _convert_to_cache to return a browse record list from command list or id list for x2many fields
                values = self.env['mail.compose.message']._convert_to_cache(values)
                composer.write(values)
                composer.send_mail(auto_commit=False)
        else:
            raise Warning("Template not found")
        return True
