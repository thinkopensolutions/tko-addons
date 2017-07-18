# -*- encoding: utf-8 -*-
from odoo import fields, api, models, _
class ProjectTeam(models.Model):
    _name = 'project.team'

    name = fields.Char('Name', required =True)
    type = fields.Selection([('b',u'Bucket'),('p',u'Prorate')], default='p', required =True)
    user_ids = fields.Many2many('res.users','project_team_users_rel','team_id','user_id', string=u'Users')
