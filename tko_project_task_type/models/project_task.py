# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields
from lxml import etree


class task_type(models.Model):
    _name = 'task.type'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer('Color Index', size=1)
    task_id = fields.Many2one('project.task', string='Task')


class project_task(models.Model):
    _inherit = 'project.task'

    type_name = fields.Char(
        compute='_get_type_name',
        store=True,
        string='Name')
    task_type_id = fields.Many2one('task.type', string='Type')
    color = fields.Integer(compute='_get_color', string='Color', store=False)

    @api.multi
    def name_get(self):
        result = []
        for task in self:
            task_type = task.task_type_id and task.task_type_id.name or ''
            result.append(
                (task.id, "%s %s" %
                 ('[' + task_type + ']', task.name or ' ')))
        return result

    @api.depends('task_type_id.name')
    def _get_type_name(self):
        for record in self:
            if record.task_type_id:
                record.type_name = record.task_type_id.name

    @api.depends('task_type_id.color')
    def _get_color(self):
        for record in self:

            if record.task_type_id:
                record.color = record.task_type_id.color

    @api.onchange('task_type_id')
    def _change_task_type(self):
        result = {'value': {}}
        if self.task_type_id:
            result['value'].update({
                'color': str(self.task_type_id.color)[-1],
                'type_name': self.task_type_id.name,

            })
        return result

    @api.onchange('project_id')
    def _onchange_project(self):
        self.task_type_id = False
        res = super(project_task, self)._onchange_project()
        task_type_ids = self.project_id and self.project_id.task_type_ids and self.project_id.task_type_ids.ids or []
        return {'domain': {'task_type_id': [('id', 'in', task_type_ids)]}}


class ProjectProject(models.Model):
    _inherit = 'project.project'

    task_type_ids = fields.Many2many('task.type', string="Task Type")
