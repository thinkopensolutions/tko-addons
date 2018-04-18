# -*- coding: utf-8 -*-

from openerp import models, osv, fields, api, _
from collections import Counter


class survey_question(models.Model):
    _name = 'survey.question'
    _inherit = 'survey.question'

    type = fields.Selection(selection_add=[('integer_box', 'Integer Value')])
    student_fields = fields.Many2one(
        'ir.model.fields',
        string="Related to Student field",
        inverse="change_lead_field",
        domain="[('model_id.model','=', 'op.student'),('ttype','in', ['char', 'text', 'date' ,'datetime', 'integer', 'float', 'selection'])]",
    )

    @api.multi
    def change_lead_field(self):
        for rec in self:
            field_obj = self.env['ir.model.fields'].browse(rec.student_fields.id)
            if field_obj.ttype == 'char':
                rec.type = 'textbox'
            elif field_obj.ttype == 'text':
                rec.type = 'free_text'
            elif field_obj.ttype == 'float':
                rec.type = 'numerical_box'
            elif field_obj.ttype == 'integer':
                rec.type = 'integer_box'
            elif field_obj.ttype == 'datetime' or field_obj.ttype == 'date':
                rec.type = 'datetime'
            elif field_obj.ttype == 'selection':
                rec.type = 'simple_choice'
            """else:
                self.type = 'textbox'"""


class survey_user_input(models.Model):
    ''' Metadata for a set of one student's answers to a particular survey '''
    _inherit = "survey.user_input"

    student_id = fields.Many2one('op.student', string="About Student:", readonly=True)

    # Set Student in User Input
    @api.model
    def create(self, vals):
        if 'partner_id' in vals.keys() and vals['partner_id']:
            student = self.env['op.student'].search([('partner_id', '=', vals['partner_id'])], limit=1)
            if len(student):
                vals.update({'student_id': student.id})
        return super(survey_user_input, self).create(vals)

    # Set Student in User Input
    @api.multi
    def write(self, vals):
        if 'partner_id' in vals.keys() and vals['partner_id']:
            student = self.env['op.student'].search([('partner_id', '=', vals['partner_id'])], limit=1)
            if len(student):
                vals.update({'student_id': student.id})
        return super(survey_user_input, self).write(vals)


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'

    student_id = fields.Many2one(related='user_input_id.student_id',
                                 store=True)

    # Write Student related fields on op.student object
    @api.model
    def add_survey_to_student_save_line(self, user_input_id, question, post, answer_tag):
        if question.student_fields:
            if post[answer_tag]:
                user_input_obj = self.env['survey.user_input'].browse(user_input_id)
                student_values = {
                    question.student_fields.name: post[answer_tag],
                }
                user_input_obj.student_id.write(student_values)
        return True

    @api.model
    def save_line_free_text(self, user_input_id, question, post, answer_tag):
        self.add_survey_to_student_save_line(user_input_id, question, post, answer_tag)
        return super(SurveyUserInputLine, self).save_line_free_text(user_input_id, question, post, answer_tag)

    @api.model
    def save_line_textbox(self, user_input_id, question, post, answer_tag):
        self.add_survey_to_student_save_line(user_input_id, question, post, answer_tag)
        return super(SurveyUserInputLine, self).save_line_textbox(user_input_id, question, post, answer_tag)

    @api.model
    def save_line_numerical_box(self, user_input_id, question, post, answer_tag):
        self.add_survey_to_student_save_line(user_input_id, question, post, answer_tag)
        return super(SurveyUserInputLine, self).save_line_numerical_box(user_input_id, question, post, answer_tag)

    @api.model
    def save_line_datetime(self, user_input_id, question, post, answer_tag):
        self.add_survey_to_student_save_line(user_input_id, question, post, answer_tag)
        return super(SurveyUserInputLine, self).save_line_datetime(user_input_id, question, post, answer_tag)

    @api.model
    def save_line_simple_choice(self,user_input_id, question, post, answer_tag):
        old_value = False
        if answer_tag in post and post[answer_tag].strip() != '':
            old_value = post[answer_tag]
            selection_field_name = question.student_fields.name
            # get selection values and convert to dict
            if selection_field_name:
                selection_dict = dict(self.env['op.student']._fields[str(selection_field_name)]._column_selection)
                selection_dict_inv = {v: k for k, v in selection_dict.iteritems()}
                key = self.env['survey.label'].browse(int(post[answer_tag])).value
                if selection_dict_inv.get(key):
                    post[answer_tag] = selection_dict_inv[key]
                    self.add_survey_to_student_save_line(user_input_id, question, post, answer_tag)
        if old_value:
            post[answer_tag] = old_value
        return super(SurveyUserInputLine, self).save_line_simple_choice(user_input_id, question, post, answer_tag)

    # @api.model
    # def save_line_multiple_choice(self, user_input_id, question, post, answer_tag):
    #     self.add_survey_to_student_save_line(user_input_id, question, post, answer_tag)
    #     return super(SurveyUserInputLine, self).save_line_multiple_choice(user_input_id, question, post, answer_tag)

    @api.model
    def save_line_integer_box(self, user_input_id, question, post, answer_tag):

        self.add_survey_to_student_save_line(user_input_id, question, post, answer_tag)

        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'page_id': question.page_id.id,
            'survey_id': question.survey_id.id,
            'skipped': False
        }
        if answer_tag in post and post[answer_tag].strip() != '':
            vals.update({'answer_type': 'integer', 'value_integer': int(post[answer_tag])})
        else:
            vals.update({'answer_type': None, 'skipped': True})
        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])

        if old_uil:
            old_uil.write(vals)
        else:
            self.create(vals)
        return True
