# -*- coding: utf-8 -*-

import json
import logging
from openerp import SUPERUSER_ID
import werkzeug
import werkzeug.utils
from datetime import datetime
from math import ceil

from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as DTF, ustr

from openerp.addons.survey.controllers.main import WebsiteSurvey as HomeWebsiteSurvey

_logger = logging.getLogger(__name__)

class WebsiteSurvey(HomeWebsiteSurvey):
    # Survey start
    @http.route(['/survey/start/<model("survey.survey"):survey>',
                 '/survey/start/<model("survey.survey"):survey>/<string:token>'],
                type='http', auth='public', website=True)
    def start_survey(self, survey, token=None, **post):
        cr, uid, context = request.cr, request.uid, request.context
        uid = SUPERUSER_ID # to search the created Survey
        survey_obj = request.registry['survey.survey']
        user_input_obj = request.registry['survey.user_input']

        # Test mode
        if token and token == "phantom":
            _logger.info("[survey] Phantom mode")
            user_input_id = user_input_obj.create(cr, uid, {'survey_id': survey.id, 'test_entry': True}, context=context)
            user_input = user_input_obj.browse(cr, uid, [user_input_id], context=context)[0]
            data = {'survey': survey, 'page': None, 'token': user_input.token}
            return request.website.render('survey.survey_init', data)
        # END Test mode

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(cr, uid, request, survey_obj, survey, user_input_obj, context=context)
        if errpage:
            return errpage

        # Manual surveying
        if not token:
            vals = {'survey_id': survey.id}
            if request.website.user_id.id != uid:
                vals['partner_id'] = request.registry['res.users'].browse(cr, uid, uid, context=context).partner_id.id
                if post.get('lead'):
                    vals['lead_id'] = post['lead']
            user_input_id = user_input_obj.create(cr, uid, vals, context=context)
            user_input = user_input_obj.browse(cr, uid, [user_input_id], context=context)[0]
        else:
            try:
                user_input_id = user_input_obj.search(cr, uid, [('token', '=', token)], context=context)[0]
            except IndexError:  # Invalid token
                return request.website.render("website.403")
            else:
                user_input = user_input_obj.browse(cr, uid, [user_input_id], context=context)[0]

        # Do not open expired survey
        errpage = self._check_deadline(cr, uid, user_input, context=context)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # Intro page
            data = {'survey': survey, 'page': None, 'token': user_input.token}
            if post.get('lead'):
                data.update({'lead': post['lead']})
            return request.website.render('survey.survey_init', data)
        else:
            lang = ''
            if request.registry['res.users'].browse(cr, uid, uid, context=context).lang:
               lang = '/'+request.registry['res.users'].browse(cr, uid, uid, context=context).lang

            if post.get('lead'):
                return request.redirect(lang+'/survey/fill_lead/%s/%s' % (survey.id, post['lead']))
            else:
                return request.redirect(lang+'/survey/fill/%s/%s' % (survey.id, user_input.token))


    # Survey displaying for lead
    @http.route(['/survey/fill_lead/<model("survey.survey"):survey>/<string:lead>',
                 '/survey/fill_lead/<model("survey.survey"):survey>/<string:lead>/<string:prev>'],
                type='http', auth='public', website=True)
    def fill_survey_lead(self, survey, lead, prev=None, **post):
        '''Display and validates a survey'''
        cr, uid, context = request.cr, request.uid, request.context
        uid = SUPERUSER_ID
        survey_obj = request.registry['survey.survey']
        user_input_obj = request.registry['survey.user_input']
        lead_obj = request.registry['crm.lead']

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(cr, uid, request, survey_obj, survey, user_input_obj, context=context)
        if errpage:
            return errpage

        # Load the user_input
        try:
            user_input_id = user_input_obj.search(cr, uid, [('lead_id.id','=', lead)], order='write_date desc', limit=1, context=context)
        except IndexError:  # Invalid lead
            return request.website.render("website.403")
        else:
            user_input = user_input_obj.browse(cr, uid, user_input_id, context=context)[0]

        # Do not display expired survey (even if some pages have already been
        # displayed -- There's a time for everything!)
        errpage = self._check_deadline(cr, uid, user_input, context=context)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # First page
            page, page_nr, last = survey_obj.next_page(cr, uid, user_input, 0, go_back=False, context=context)
            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'lead': lead}

            if last:
                data.update({'last': True})
            return request.website.render('survey.survey', data)
        elif user_input.state == 'done':  # Display success message
            return request.website.render('survey.sfinished', {'survey': survey,
                                                               'token': user_input.token,
                                                               'user_input': user_input,
                                                               'lead': lead})
        elif user_input.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            page, page_nr, last = survey_obj.next_page(cr, uid, user_input, user_input.last_displayed_page_id.id, go_back=flag, context=context)

            #special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not page:
                page, page_nr, last = survey_obj.next_page(cr, uid, user_input, user_input.last_displayed_page_id.id, go_back=True, context=context)

            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'lead': lead}
            if last:
                data.update({'last': True})
            return request.website.render('survey.survey', data)
        else:
            return request.website.render("website.403")

    # AJAX prefilling of a survey
    @http.route(['/survey/prefill/<model("survey.survey"):survey>/<string:token>',
                 '/survey/prefill/<model("survey.survey"):survey>/<string:token>/<model("survey.page"):page>'],
                type='http', auth='public', website=True)
    def prefill(self, survey, token, page=None, **post):
        cr, uid, context = request.cr, request.uid, request.context
        uid = SUPERUSER_ID
        user_input_line_obj = request.registry['survey.user_input_line']
        ret = {}

        # Fetch previous answers
        if page:
            ids = user_input_line_obj.search(cr, uid, [('user_input_id.token', '=', token), ('page_id', '=', page.id)], context=context)
        else:
            ids = user_input_line_obj.search(cr, uid, [('user_input_id.token', '=', token)], context=context)
        previous_answers = user_input_line_obj.browse(cr, uid, ids, context=context)

        # Return non empty answers in a JSON compatible format
        for answer in previous_answers:
            if not answer.skipped:
                answer_tag = '%s_%s_%s' % (answer.survey_id.id, answer.page_id.id, answer.question_id.id)
                answer_value = None
                if answer.answer_type == 'free_text':
                    answer_value = answer.value_free_text
                elif answer.answer_type == 'text' and answer.question_id.type == 'textbox':
                    answer_value = answer.value_text
                elif answer.answer_type == 'text' and answer.question_id.type != 'textbox':
                    # here come comment answers for matrices, simple choice and multiple choice
                    answer_tag = "%s_%s" % (answer_tag, 'comment')
                    answer_value = answer.value_text
                elif answer.answer_type == 'number':
                    answer_value = answer.value_number.__str__()
                elif answer.answer_type == 'integer':
                    answer_value = answer.value_integer
                elif answer.answer_type == 'date':
                    answer_value = answer.value_date
                elif answer.answer_type == 'suggestion' and not answer.value_suggested_row:
                    answer_value = answer.value_suggested.id
                elif answer.answer_type == 'suggestion' and answer.value_suggested_row:
                    answer_tag = "%s_%s" % (answer_tag, answer.value_suggested_row.id)
                    answer_value = answer.value_suggested.id
                if answer_value:
                    dict_soft_update(ret, answer_tag, answer_value)
                else:
                    _logger.warning("[survey] No answer has been found for question %s marked as non skipped" % answer_tag)
        return json.dumps(ret)

    # AJAX prefilling of a survey
    @http.route(['/survey/prefill_lead/<model("survey.survey"):survey>/<string:lead>',
                 '/survey/prefill_lead/<model("survey.survey"):survey>/<string:lead>/<model("survey.page"):page>'],
                type='http', auth='public', website=True)
    def prefill_lead(self, survey, lead, page=None, **post):
        cr, uid, context = request.cr, request.uid, request.context
        user_input_line_obj = request.registry['survey.user_input_line']
        questions_obj = request.registry['survey.question']
        ret = {}

        lead_obj = request.registry['crm.lead'].browse(cr, uid, int(lead), context=context)[0]
        pages = request.registry['survey.page'].search(cr, uid, [('survey_id','=',survey.id)], context=context)
        guestions_ids = questions_obj.search(cr, uid, [('page_id','in',pages)], context=context)
        questions = questions_obj.browse(cr, uid, guestions_ids, context=context)
        for question in questions:
            answer_tag = '%s_%s_%s' % (survey.id, question.page_id.id, question.id)
            answer_value = None
            if question.lead_fields.id:
                field = question.lead_fields.name
                if lead_obj.__getattribute__(field):
                    answer_value = lead_obj.__getattribute__(field)
                if answer_value:
                    dict_soft_update(ret, answer_tag, answer_value)
                else:
                    _logger.warning("[survey] No answer has been found for question %s marked as non skipped" % answer_tag)
        return json.dumps(ret)

    # AJAX submission of a page
    @http.route(['/survey/submit/<model("survey.survey"):survey>'],
                type='http', methods=['POST'], auth='public', website=True)
    def submit(self, survey, **post):
        _logger.debug('Incoming data: %s', post)
        page_id = int(post['page_id'])
        cr, uid, context = request.cr, request.uid, request.context
        uid = SUPERUSER_ID
        survey_obj = request.registry['survey.survey']
        questions_obj = request.registry['survey.question']
        questions_ids = questions_obj.search(cr, uid, [('page_id', '=', page_id)], context=context)
        questions = questions_obj.browse(cr, uid, questions_ids, context=context)

        # Answer validation
        errors = {}
        for question in questions:
            answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
            errors.update(questions_obj.validate_question(cr, uid, question, post, answer_tag, context=context))

        ret = {}
        if (len(errors) != 0):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            # Store answers into database
            user_input_obj = request.registry['survey.user_input']

            user_input_line_obj = request.registry['survey.user_input_line']
            try:
                user_input_id = user_input_obj.search(cr, uid, [('token', '=', post['token'])], context=context)[0]
            except KeyError:  # Invalid token
                return request.website.render("website.403")
            for question in questions:
                answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                user_input_line_obj.save_lines(cr, uid, user_input_id, question, post, answer_tag, context=context)

            user_input = user_input_obj.browse(cr, uid, user_input_id, context=context)
            go_back = post['button_submit'] == 'previous'
            go_back_lead = post['button_submit'] == 'lead_back'
            next_page, _, last = survey_obj.next_page(cr, uid, user_input, page_id, go_back=go_back, context=context)
            vals = {'last_displayed_page_id': page_id}
            if next_page is None and not go_back:
                vals.update({'state': 'done'})
            else:
                vals.update({'state': 'skip'})
            user_input_obj.write(cr, uid, user_input_id, vals, context=context)

            lang = ''
            if request.registry['res.users'].browse(cr, uid, uid, context=context).lang:
               lang = '/'+request.registry['res.users'].browse(cr, uid, uid, context=context).lang


            if post.get('lead'):
                ret['redirect'] = '/survey/fill_lead/%s/%s' % (survey.id, post['lead'])
            else:
                ret['redirect'] = lang+'/survey/fill/%s/%s' % (survey.id, post['token'])
            if go_back:
                ret['redirect'] += '/prev'
            if go_back_lead:
                ret['redirect'] = '/web#id=%s&action=add_survey_to_crm.action_back_to_lead' % (post['lead'])
        return json.dumps(ret)

def dict_soft_update(dictionary, key, value):
    ''' Insert the pair <key>: <value> into the <dictionary>. If <key> is
    already present, this function will append <value> to the list of
    existing data (instead of erasing it) '''
    if key not in dictionary:
        dictionary.update({key: [value]})