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

from odoo import models, fields
from odoo.addons.base.ir.ir_mail_server import extract_rfc2822_addresses


class ir_mail_server(models.Model):
    _inherit = 'ir.mail_server'

    user_id = fields.Many2one('res.users', string='Owner')

    _sql_constraints = [
        ('smtp_user_uniq', 'unique(user_id)', 'That user already has a SMTP server.')
    ]

    def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None, smtp_user=None,
                   smtp_password=None, smtp_encryption=None, smtp_debug=False):
        from_rfc2822 = extract_rfc2822_addresses(message['From'])[-1]
        server_id = self.env['ir.mail_server'].search([('smtp_user', '=', from_rfc2822)])
        if server_id and server_id[0]:
            message['Return-Path'] = from_rfc2822
        return super(ir_mail_server, self).send_email(message, mail_server_id, smtp_server, smtp_port,
                                                      smtp_user, smtp_password, smtp_encryption, smtp_debug)


class mail_mail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for email in self.env['mail.mail'].browse(self.ids):
            from_rfc2822 = extract_rfc2822_addresses(email.email_from)[-1]
            server_id = self.env['ir.mail_server'].search([('smtp_user', '=', from_rfc2822)])
            server_id = server_id and server_id[0] or False
            if server_id:
                self.write({'mail_server_id': server_id[0].id, 'reply_to': email.email_from})
        return super(mail_mail, self).send(auto_commit=auto_commit, raise_exception=raise_exception)
