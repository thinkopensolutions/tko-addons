# -*- coding: utf-8 -*-
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Thinkopen - Brasil
#    Copyright (C) Thinkopen Solutions (<http://www.thinkopensolutions.com.br>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api


class MailTemplate(models.Model):
    "Templates for sending email"
    _inherit = "mail.template"

    group_ids = fields.Many2many('res.groups', 'mail_template_groups_rel', 'template_id', 'group_id', string='Groups')
    template_user_ids = fields.Many2many('res.users', 'mail_template_user_ids_rel','template_id','user_id',compute='get_template_user_ids', string='Users',store=True)

    @api.one
    @api.depends('group_ids.users')
    def get_template_user_ids(self):
        user_ids = []

        for group in self.group_ids:
            for user in group.users:
                if user.id not in user_ids:
                    user_ids.append(user.id)
        if not self.group_ids:
            user_ids = self.env['res.users'].search([('active','=',True)]).ids
        self.template_user_ids = [(6, 0, user_ids)]

