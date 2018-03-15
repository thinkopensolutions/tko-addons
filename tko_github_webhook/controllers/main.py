# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen - Portugal & Brasil
#    Copyright (C) Thinkopen Solutions (<http://www.thinkopensolutions.com>).
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

import openerp.http as http
from openerp.http import request
import logging

_logger = logging.getLogger(__name__)


class GithubWebhook(http.Controller):
    @http.route('/webhooks/github', type='json', auth='public',
                methods=['POST'])
    def github_webhook(self, **kwargs):
        values = {}
        # Gather data
        try:
            values['payload'] = request.get_json()
            request.env['github.webhook'].sudo().create(values)
        except Exception:
            logging.warning('Request parsing failed')
            abort(400)

        return "<Response></Response>"
