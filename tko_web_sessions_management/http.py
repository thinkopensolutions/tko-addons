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
import odoo
from dateutil.relativedelta import *
from odoo import SUPERUSER_ID
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug.wsgi import wrap_file
from odoo.http import request
from odoo.tools.func import lazy_property
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

#
_logger = logging.getLogger(__name__)


class OpenERPSession(odoo.http.OpenERPSession):
    def logout(self, keep_db=False, logout_type=None, env=None):
        try:
            env = env or request.env
        except:
            pass
        if env and hasattr(
                env,
                'registry') and env.registry.get('ir.sessions'):
            session = env['ir.sessions'].sudo().search(
                [('session_id', '=', self.sid),
                 ('logged_in', '=', True), ])
            if session:
                session._on_session_logout(logout_type)
        return super(OpenERPSession, self).logout(keep_db=keep_db)


class Root_tkobr(odoo.http.Root):
    @lazy_property
    def session_store(self):
        # Setup http sessions
        path = odoo.tools.config.session_dir
        _logger.debug('HTTP sessions stored in: %s', path)
        return werkzeug.contrib.sessions.FilesystemSessionStore(
            path, session_class=OpenERPSession)


root = Root_tkobr()
odoo.http.root.session_store = root.session_store
