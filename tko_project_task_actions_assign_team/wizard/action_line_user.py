# -*- encoding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import Warning


class ActionLineWizard(models.TransientModel):
    _inherit = 'action.line.wizard'

    user_id = fields.Many2one('res.users', string='User', required=True)

    @api.model
    def default_get(self, fields):
        context = self.env.context
        active_ids =context.get('active_ids', [])
        records = self.env['project.task.action.line'].browse(active_ids)
        if len(records):
            team = records[0].team_id
            if not all(team == record.team_id for record in records):
                raise Warning(u"Please select action lines with same team")
        return super(ActionLineWizard, self).default_get(fields)

