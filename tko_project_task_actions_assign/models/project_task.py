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

from odoo import models, api, fields
from openerp.exceptions import ValidationError

class ProjectTaskActions(models.Model):
	_inherit = 'project.task.action'

	user_id = fields.Char(string="Assigned To")


class ProjectTaskActionsLine(models.Model):
	_inherit = 'project.task.action.line'

	user_id = fields.Many2one('res.users',string="Assigned To", compute='onchange_action', store=True)
	state = fields.Selection(selection_add=[('n', u'New')])

	@api.one
	def self_assign(self):
		self.user_id = self.env.uid

	@api.one
	@api.depends('action_id')
	def onchange_action(self):
		res = super(ProjectTaskActionsLine, self).onchange_action()
		flag =False
		user_id = False
		try:
			user_id = self and self.task_id and self.task_id.project_id and self.action_id and self.action_id.user_id and eval('self.'+self.action_id.user_id) or False
		except Exception as e:
			flag = True
		if (user_id and user_id._name != 'res.users') or flag:
			raise ValidationError("Please set proper user id in " + self.action_id.name)
		self.user_id = user_id and user_id.id or False


	@api.multi
	def set_done(self):
		if self.user_id.id == self._uid:
			return super(ProjectTaskActionsLine , self).set_done()
		else:
			raise ValidationError("This user have no rights to input a time. Only " + self.user_id.name  +" can done it")

	def set_cancel(self):
		if self.user_id.id == self._uid:
			return super(ProjectTaskActionsLine , self).set_cancel()
		else:
			raise ValidationError("This user have no rights to input a time. Only " + self.user_id.name  +" can cancle it")


class ProjectTask(models.Model):
	_inherit = 'project.task'

	user_ids = fields.Many2many('res.users',string='Team',compute='get_users')

	@api.multi
	def get_users(self):
		for task in self:
			user_ids = []
			for action_line in task.action_line_ids:
				if action_line.user_id:
					user_ids.append(action_line.user_id.id)
			task.user_ids = [(6, 0 , list(set(user_ids)))]
