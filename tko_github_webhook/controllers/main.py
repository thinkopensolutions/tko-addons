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

import hmac
import json
import logging
from hashlib import sha1
from sys import hexversion

import odoo.http as http
from odoo.http import request

_logger = logging.getLogger(__name__)


class GithubWebhook(http.Controller):
    @http.route('/webhooks/github', type='json', auth="none",
                methods=['POST'], website=True, csrf=False)
    def github_webhook(self, **kw):
        secret = request.env['ir.config_parameter'].sudo().get_param('github.webhook.token')
        if secret:
            # Only SHA1 is supported
            header_signature = request.httprequest.headers.get('X-Hub-Signature')
            if header_signature is None:
                http.Response.status = '403'
                return {'error': 'Authentication error.'}

            sha_name, signature = header_signature.split('=')
            if sha_name != 'sha1':
                http.Response.status = '501'
                return {'error': 'Authentication error.'}

            # HMAC requires the key to be bytes, but data is string
            mac = hmac.new(str(secret), msg=request.httprequest.data, digestmod=sha1)

            # Python prior to 2.7.7 does not have hmac.compare_digest
            if hexversion >= 0x020707F0:
                if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
                    http.Response.status = '403'
                    return {'error': 'Authentication error.'}
            else:
                # What compare_digest provides is protection against timing
                # attacks; we can live without this protection for a web-based
                # application
                if not str(mac.hexdigest()) == str(signature):
                    http.Response.status = '403'
                    return {'error': 'Authentication error.'}
        try:
            payload = request.jsonrequest
            request.env['github.webhook'].sudo().create({
                'name': dict(payload).get('repository', {}).get('name', 'unknown'),
                'payload': json.dumps(request.jsonrequest,
                                      indent=2,
                                      sort_keys=True)})
        except Exception:
            _logger.error('Request parsing failed')
            http.Response.status = '400'
            return {'error': 'Request parsing failed'}
        return True
