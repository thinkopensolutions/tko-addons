# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.base.ir.ir_mail_server import extract_rfc2822_addresses


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    user_id = fields.Many2one('res.users', string='Owner')

    _sql_constraints = [
        ('smtp_user_uniq', 'unique(user_id)',
         'That user already has a SMTP server.')
    ]

    def send_email(self, message, mail_server_id=None,
                   smtp_server=None, smtp_port=None, smtp_user=None,
                   smtp_password=None, smtp_encryption=None,
                   smtp_debug=False):
        from_rfc2822 = extract_rfc2822_addresses(message['From'])[-1]
        server_id = self.env['ir.mail_server'].search([
            ('smtp_user', '=', from_rfc2822)])
        if server_id and server_id[0]:
            if 'Return-Path' in message:
                message.replace_header('Return-Path', from_rfc2822)
        return super(IrMailServer, self).send_email(message, mail_server_id,
                                                    smtp_server, smtp_port,
                                                    smtp_user, smtp_password,
                                                    smtp_encryption,
                                                    smtp_debug)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    def send(self, auto_commit=False, raise_exception=False):
        for email in self.env['mail.mail'].browse(self.ids):
            from_rfc2822 = extract_rfc2822_addresses(email.email_from)[-1]
            server_id = self.env['ir.mail_server'].search([
                ('smtp_user', '=', from_rfc2822)])
            server_id = server_id and server_id[0] or False
            if server_id:
                self.write(
                    {'mail_server_id': server_id[0].id,
                     'reply_to': email.email_from})
        return super(MailMail, self).send(auto_commit=auto_commit,
                                          raise_exception=raise_exception)
