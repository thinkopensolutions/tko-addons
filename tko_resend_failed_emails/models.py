# -*- coding: utf-8 -*-
from odoo import api, models, fields


class MailMessage(models.Model):
    _inherit = 'mail.message'

    sent_failed = fields.Boolean('Sent', compute="_compute_sent_failed", default=False,
                                 help='Was message sent to someone', store=True)

    @api.depends('author_id', 'partner_ids')
    def _compute_sent_failed(self):
        for r in self:
            r_sudo = r.sudo()
            sent_failed = len(r_sudo.partner_ids) > 1 \
                          or len(r_sudo.partner_ids) == 1 \
                          and r_sudo.author_id \
                          and r_sudo.partner_ids[0].id != r_sudo.author_id.id
            mail = self.env['mail.mail'].search([('mail_message_id', '=', r.id)])
            # If there is a mail associated to message and state is Exception
            if mail and mail.state == 'exception' and sent_failed:
                r.sent_failed = sent_failed

    @api.multi
    def message_format(self):
        message_values = super(MailMessage, self).message_format()
        message_index = {message['id']: message for message in message_values}
        for item in self:
            msg = message_index.get(item.id)
            if msg:
                msg['sent_failed'] = item.sent_failed
        return message_values

    def resend_failed_emails(self, message_id=False):
        if not message_id:
            message_id = self.env.context.get('message_id', False)
        if message_id:
            mail = self.env['mail.mail'].search([('mail_message_id', '=', int(message_id))])
            if mail.state != 'outgoing':
                mail.mark_outgoing()
            # not sending immediately, it doesn't update mail wall correctly
            # mail.send()
        return True


class MailMail(models.Model):
    _inherit = 'mail.mail'

    ## update value of sent_failed, in mail_message object
    @api.multi
    def write(self, vals):
        super(MailMail, self).write(vals)
        for record in self:
            message = self.env['mail.message'].browse(record.mail_message_id.id)
            if record.state == 'exception':
                message.sent_failed = True
            else:
                message.sent_failed = False
        return True
