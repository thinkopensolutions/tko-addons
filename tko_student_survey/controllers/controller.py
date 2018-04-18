# -*- coding: utf-8 -*-

import json
import logging
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
                print "post...................",post
                if post.get('lead'):
                    vals['student_id'] = post['lead']
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

            return request.redirect(lang+'/survey/fill/%s/%s' % (survey.id, user_input.token))

