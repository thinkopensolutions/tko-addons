# -*- encoding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import Warning


class ActionLineWizard(models.TransientModel):
    _inherit = 'action.line.wizard'

    team_id = fields.Many2one('project.team', string='Team', required=True)

    @api.model
    def default_get(self, fields):
        result = super(ActionLineWizard, self).default_get(fields)
        context = self.env.context
        active_ids =context.get('active_ids', [])
        records = self.env['project.task.action.line'].browse(active_ids)
        if len(records):
            team = records[0].team_id
            if not all(team == record.team_id for record in records):
                raise Warning(u"Please select action lines with same team")

        result.update({'team_id': len(records) and records[0].team_id and records[0].team_id.id or False})
        return result


    @api.onchange('team_id')
    def onchange_team(self):
        result = {}
        user_ids = self.team_id and self.team_id.user_ids.ids or []
        result['domain'] = {'user_id' : [('id','in',user_ids)]}
        return result



