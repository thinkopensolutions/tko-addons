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

from openerp.osv import osv, fields

AVAILABLE_STATES = [('new', 'Not started yet'),
                    ('skip', 'Partially completed'),
                    ('done', 'Completed')]


class crm_lead(osv.osv):
    def _get_survey_answer(self, cr, uid, ids, name, unknown, context=None):
        res = {}
        for record in self.browse(cr, uid, ids):
            if record.partner_id and record.survey_id:
                suvery_answer = self.pool.get('survey.user_input').search(cr, uid,
                                                                          [('survey_id', '=', record.survey_id.id),
                                                                           ('partner_id', '=', record.partner_id.id)],
                                                                          order='id desc')
                if len(suvery_answer):
                    res[record.id] = suvery_answer[0]
        return res

    def _answer_search(self, cursor, user, obj, name, args, context=None):
        return []

    _inherit = "crm.lead"
    _columns = {
        'survey_id': fields.many2one('survey.survey', 'Survey'),
        'survey_ans_id': fields.function(_get_survey_answer,
                                         type="many2one",
                                         relation='survey.user_input',
                                         string="Survey Answer", fnct_search=_answer_search,
                                         readonly=True),
        'survey_created': fields.boolean('Survey Created'),
        'answer_state': fields.related('survey_ans_id', 'state',
                                       type="selection",
                                       selection=AVAILABLE_STATES,
                                       string="Answer State", readonly=True)

    }
    _defaults = {'survey_created': False}

    def answer_survey(self, cr, uid, ids, context=None):
        token = uuid.uuid4().__str__()
        survey_obj = self.pool.get('survey.survey')
        survey_response_obj = self.pool.get('survey.user_input')
        # create response with token
        self_obj = self.browse(cr, uid, ids[0])
        survey_id = self_obj.survey_id.id
        customer_id = self_obj.partner_id.id
        is_survey = self_obj.survey_created
        answer_state = self_obj.answer_state
        if not customer_id:
            raise osv.except_osv('Warning', 'Please select a customer for this survey')

        if not survey_id:
            raise osv.except_osv('Warning', 'Please select a survey to answer')
        # create surevey_input because survey input  has not been created for this record
        if not answer_state:
            for wizard in self.browse(cr, uid, ids):
                user_input = survey_response_obj.create(cr, uid, {
                    'survey_id': survey_id,
                    'deadline': False,
                    'date_create': datetime.now(),
                    'type': 'link',
                    'state': 'new',
                    'token': token,
                    'partner_id': wizard.partner_id.id,
                    'email': wizard.partner_id.email})

                ''' Open the website page with the survey form '''
            trail = "/" + survey_response_obj.browse(cr, uid, user_input).token
            self.write(cr, uid, ids, {'survey_created': True})
            return {
                'type': 'ir.actions.act_url',
                'name': "View Answers",
                'target': 'new',
                'url': survey_obj.browse(cr, uid, wizard.survey_id.id).public_url + trail,
            }
        else:
            user_input = self_obj.survey_ans_id.id
            trail = ""
            trail = "/" + survey_response_obj.browse(cr, uid, user_input).token
            # survey has been replied
            if self_obj.survey_ans_id.state == 'done':
                final_url = survey_obj.read(cr, uid, [survey_id], ['print_url'], context=context)[0][
                                'print_url'] + trail
            # survey has been not replied
            else:
                final_url = survey_obj.browse(cr, uid, survey_id).public_url + trail
            return {
                'type': 'ir.actions.act_url',
                'name': "Print Survey",
                'target': 'new',
                'url': final_url
            }
