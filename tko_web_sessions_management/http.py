# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
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

import logging
import openerp
from openerp.osv import fields, osv, orm
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import *
from openerp import SUPERUSER_ID
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
import simplejson
from werkzeug.wsgi import wrap_file
from openerp.http import request
from openerp.tools.translate import _
from openerp.http import Response
from openerp import http
from openerp.tools.func import lazy_property
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
#   
_logger = logging.getLogger(__name__)


class Root_tkobr(openerp.http.Root):
       
    def get_response(self, httprequest, result, explicit_session):
        now = fields.datetime.now()
        if isinstance(result, Response) and result.is_qweb:
            try:
                result.flatten()
            except(Exception), e:
                if request.db:
                    result = request.registry['ir.http']._handle_exception(e)
                else:
                    raise
           
        if isinstance(result, basestring):
            response = Response(result, mimetype='text/html')
        else:
            response = result
           
        if httprequest.session.should_save:
            self.session_store.save(httprequest.session)
#          We must not set the cookie if the session id was specified using a http header or a GET parameter.
#          There are two reasons to this:
#          - When using one of those two means we consider that we are overriding the cookie, which means creating a new
#            session on top of an already existing session and we don't want to create a mess with the 'normal' session
#            (the one using the cookie). That is a special feature of the Session Javascript class.
#          - It could allow session fixation attacks.
        max_seconds = 90 * 24 * 60 * 60
        if not explicit_session and hasattr(response, 'set_cookie') and (httprequest.method == 'POST' and httprequest.path <> '/longpolling/poll' or httprequest.method == 'GET'):
            if httprequest.session.uid:
                cr = openerp.registry(request.cr.dbname).cursor()
                # autocommit: our single update request will be performed atomically.
                # (In this way, there is no opportunity to have two transactions
                # interleaving their cr.execute()..cr.commit() calls and have one
                # of them rolled back due to a concurrent access.)
                cr.autocommit(True)
                session_obj = request.registry.get('ir.sessions')
                if session_obj:
                    session_id = session_obj.search(cr, openerp.SUPERUSER_ID,
                        [('session_id', '=', httprequest.session.sid),
                         ('expiration_date', '>', now)],
                        order='expiration_date asc',
                        limit=1,
                        context=request.context)
                    if session_id:
                        session = session_obj.read(cr, openerp.SUPERUSER_ID,
                            session_id[0], ['logged_in',
                                            'session_seconds',
                                            'expiration_date'],
                            context=request.context)
                        seconds = session['session_seconds']
                        session_obj.write(cr, openerp.SUPERUSER_ID, session['id'],
                            {'expiration_date': datetime.strftime((datetime.strptime(now, DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(seconds=seconds)), DEFAULT_SERVER_DATETIME_FORMAT),},
                            context=request.context)
                        cr.commit()
                        response.set_cookie('session_id', httprequest.session.sid, max_age=max_seconds)
                    else: #no session id in database, not logged in yet
                        #cr.close()
                        # Most IE and Safari versions decided not to preserve location.hash upon
                        # redirect. And even if IE10 pretends to support it, it still fails
                        # inexplicably in case of multiple redirects (and we do have some).
                        # See extensive test page at http://greenbytes.de/tech/tc/httpredirects/
                        url = '/web/session/logout'
                        code = 303
                        #if request.httprequest.user_agent.browser in ('firefox',):
                        request.session.logout(keep_db=True)
                        #response.set_cookie('session_id', httprequest.session.sid, max_age=max_seconds)
                        return werkzeug.utils.redirect(url, code)
                        #return "<html><head><script>window.location = '%s' + location.hash;</script></head></html>" % url
                        #response.set_cookie('session_id', httprequest.session.sid, max_age=max_seconds)
                else:
                    response.set_cookie('session_id', httprequest.session.sid, max_age=max_seconds)
                cr.close()
            else: #no session uid, not logged in yet
                response.set_cookie('session_id', httprequest.session.sid, max_age=max_seconds)
        return response
       
openerp.http.Root.get_response = Root_tkobr().get_response

