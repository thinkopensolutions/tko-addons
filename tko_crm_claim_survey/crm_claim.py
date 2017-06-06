# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import uuid
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
# from openerp.osv import osv, fields
from openerp import models, fields, api, _

AVAILABLE_STATES = [('new', 'Not started yet'),
                    ('skip', 'Partially completed'),
                    ('done', 'Completed')]


class crm_claim(models.Model):
    _inherit = 'crm.claim'

    @api.multi
    def _get_survey_answer(self):
        res = {}
        for record in self:
            if record.partner_id and record.survey_id:
                suvery_answer = self.env['survey.user_input'].search(
                                                [('survey_id', '=', record.survey_id.id),
                                                ('partner_id', '=', record.partner_id.id)],
                                                order='id desc')
                if len(suvery_answer):
                    res[record.id] = suvery_answer[0]
        return res

    # def _answer_search(self, cursor, user, obj, name, args, context=None):
    @api.multi
    def _answer_search(self):
        return []

    survey_id = fields.Many2one('survey.survey', 'Survey')
    survey_ans_id = fields.Many2one(compute=_get_survey_answer, relation='survey.user_input',
                            string="Survey Answer", fnct_search=_answer_search
                             )
    survey_created = fields.Boolean('Survey Created', default= False)
    answer_state = fields.Selection(related='survey_id.user_input_ids.state', selection=AVAILABLE_STATES,
                                       string="Answer State", readonly=True,store=True)
    # _defaults = {'survey_created': False}

    @api.onchange('type_id', 'survey_id')
    def onchange_type(self):
        res = {}
        survey_id = False
        survey_ids = []
        if self.type_id:
            for survey in self.type_id.survey_ids:
                survey_ids.append(survey.id)
            self.survey_id = survey_ids and survey_ids[0]
        # show all surveys
        if not len(survey_ids):
            survey_ids = self.env['survey.survey'].search([])
        res['domain'] = {'survey_id': [('id', 'in', survey_ids and survey_ids.ids or [])]}
        return res
    

    @api.multi
    def answer_survey(self):
        token = uuid.uuid4().__str__()
        survey_obj = self.env['survey.survey']
        survey_response_obj = self.env['survey.user_input']
        # create response with token
        self_obj = self.browse(self.id)
        survey_id = self.survey_id.id
        customer_id = self_obj.partner_id.id
        is_survey = self_obj.survey_created
        answer_state = self_obj.answer_state
        if not customer_id:
            # raise osv.except_osv('Warning', 'Please select a customer for this survey')
            raise UserError(_("Please select a customer for this survey"))
            # raise Warning(_('Please select a customer for this survey'))
        if not survey_id:
            raise UserError(_("Please select a survey to answer"))
            
            # raise Warning(_('Please select a survey to answer'))

            # raise osv.except_osv('Warning', 'Please select a survey to answer')
        # create surevey_input because survey input  has not been created for this record
        if not answer_state:
            for wizard in self.browse(ids):
                user_input = survey_response_obj.create({
                    'survey_id': survey_id,
                    'deadline': False,
                    'date_create': datetime.now(),
                    'type': 'link',
                    'state': 'new',
                    'token': token,
                    'partner_id': wizard.partner_id.id,
                    'email': wizard.partner_id.email})

                ''' Open the website page with the survey form '''
            trail = "/" + survey_response_obj.browse(user_input).token
            self.write(cr, uid, ids, {'survey_created': True})
            return {
                'type': 'ir.actions.act_url',
                'name': "View Answers",
                'target': 'new',
                'url': survey_obj.browse(wizard.survey_id.id).public_url + trail,
            }
        else:
            user_input = self_obj.survey_ans_id.id
            trail = ""
            trail = "/" + survey_response_obj.browse(user_input).token
            # survey has been replied
            if self_obj.survey_ans_id.state == 'done':
                final_url = survey_obj.read([survey_id], ['print_url'])[0][
                                'print_url'] + trail
            # survey has been not replied
            else:
                final_url = survey_obj.browse(survey_id).public_url + trail
            return {
                'type': 'ir.actions.act_url',
                'name': "Print Survey",
                'target': 'new',
                'url': final_url
            }
# on_change="onchange_template_id(template_id, composition_mode, model, res_id, context)"

class claim_type(models.Model):
    _inherit = 'claim.type'

    survey_ids = fields.Many2many('survey.survey', 'claim_type_survey_rel', 'claim_id', 'survey_id',
                                       string='Survey')
