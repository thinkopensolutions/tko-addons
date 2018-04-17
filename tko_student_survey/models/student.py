# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api
from openerp.exceptions import Warning

#
# class opstudent(models.Model):
#     _inherit = ['mail.thread', 'ir.needaction_mixin']
#

class opstudent1(models.Model):
    _inherit = 'op.student'

    survey_id = fields.Many2one('survey.survey', u'Survey')
    survey_input_lines = fields.One2many(
        comodel_name='survey.user_input_line', inverse_name='student_id',
        string='Surveys answers')
    survey_inputs = fields.One2many(
        comodel_name='survey.user_input', inverse_name='student_id',
        string='Surveys')
    survey_input_count = fields.Integer(
        string='Survey number', compute='_count_survey_input',
        store=True)

    @api.one
    @api.depends('survey_inputs')
    def _count_survey_input(self):
        self.survey_input_count = len(self.survey_inputs)

    @api.multi
    def send_student_survey(self, survey_id):
        # Calling method from button sends context in survey_id
        # we check it to be integer value
        if not isinstance(survey_id, int):
            survey_id = False
        templates = self.env['ir.model.data'].get_object_reference('survey', 'email_template_survey')
        if len(templates):
            template_id = templates[1] if len(templates) > 0 else False
            for student in self:
                if not student.survey_id:
                    raise Warning(u"Please select survey to send!")
                composer = self.env['survey.mail.compose.message'].create({
                    'res_id': student.id,
                    'partner_ids': [(6, 0, [student.partner_id.id])],
                    'survey_id': survey_id or student.survey_id.id,
                    'template_id': template_id,
                    'composition_mode': 'comment',
                    'public' : 'email_private', # send Private email , a Token will be generated , User can do survey only after login into system
                })
                # Get mail body on from onchange_template_id
                values = composer.onchange_template_id(template_id, 'comment', 'op.student', student.id)['value']
                # use _convert_to_cache to return a browse record list from command list or id list for x2many fields
                values = self.env['mail.compose.message']._convert_to_cache(values)
                composer.write(values)
                composer.send_mail(auto_commit=False)
        else:
            raise Warning("Template not found")
        return True
