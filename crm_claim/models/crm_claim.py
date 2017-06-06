# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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

import odoo
# from odoo.addons.crm import crm
from odoo import api, fields, models, tools
from odoo import tools
from odoo.tools.translate import _
from odoo.tools import html2plaintext


class crm_case_section(models.Model):
	_name = "crm.case.section"
	_inherit = ['mail.thread']
	# _inherit = ['mail.thread', 'ir.needaction_mixin']
	_description = "Sales Teams"
	_order = "complete_name"
	_period_number = 5

	@api.multi
	def get_full_name(self):
		for section in self:
			return dict(self.name_get())


	name = fields.Char('Sales Team', size=64, required=True, translate=True)
	complete_name = fields.Char(compute=get_full_name, size=256, readonly=True, store=True)
	# complete_name = fields.Char('Complete Name')
	code = fields.Char('Code', size=8)
	active = fields.Boolean('Active', help="If the active field is set to "\
				   "false, it will allow you to hide the sales team without removing it.", default=True)
	change_responsible = fields.Boolean('Reassign Escalated', help="When escalating to this team override the salesman with the team leader.")
	user_id = fields.Many2one('res.users', 'Team Leader')
	member_ids = fields.Many2many('res.users', 'sale_member_rel', 'section_id', 'member_id', 'Team Members')
	reply_to = fields.Char('Reply-To', size=64, help="The email address put in the 'Reply-To' of all emails sent by Odoo about cases in this sales team")
	parent_id = fields.Many2one('crm.case.section', 'Parent Team')
	child_ids = fields.One2many('crm.case.section', 'parent_id', 'Child Teams')
	note = fields.Text('Description')
	working_hours = fields.Float('Working Hours', digits=(16, 2))
	color = fields.Integer('Color Index')


	_sql_constraints = [
		('code_uniq', 'unique (code)', 'The code of the sales team must be unique !')
	]

	
	@api.multi
	def name_get(self):
		res = []
		if not self._ids:
			return res
		reads = self.read(['name', 'parent_id'])

		for record in reads:
			name = record['name']
			if record['parent_id']:
				name = record['parent_id'][1] + ' / ' + name
			res.append((record['id'], name))
		return res


class crm_case_categ(models.Model):
	""" Category of Case """
	_name = "crm.case.categ"
	_description = "Category of Case"
	
	@api.multi
	def _find_object_id(self):
		"""Finds id for case object"""
		# context = context or {}
		object_id = self._context.get('object_id', False)
		crm_ids = self.env['ir.model'].search(['|', ('id', '=', object_id), ('model', '=', 'crm.claim')])
		return crm_ids and crm_ids[0] or False

	name = fields.Char('Name', required=True, translate=True)
	section_id = fields.Many2one('crm.case.section', 'Sales Team')
	object_id = fields.Many2one('ir.model', 'Object Name', default=_find_object_id)



class CrmClaimStage(models.Model):
	""" Model for claim stages. This models the main stages of a claim
		management flow. Main CRM objects (leads, opportunities, project
		issues, ...) will now use only stages, instead of state and stages.
		Stages are for example used to display the kanban view of records.
	"""
	_name = "crm.claim.stage"
	_description = "Claim stages"
	_rec_name = 'name'
	_order = "sequence"

	name = fields.Char('Stage Name', required=True, translate=True)
	sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.", default= lambda *args: 1)
	section_ids = fields.Many2many('crm.case.section', 'section_claim_stage_rel', 'stage_id', 'section_id', string='Sections',
					help="Link between stages and sales teams. When set, this limitate the current stage to the selected sales teams.")
	case_default = fields.Boolean('Common to All Teams',
					help="If you check this field, this stage will be proposed by default on each sales team. It will not assign this stage to existing teams.")


class CrmClaim(models.Model):
	""" Crm claim
	"""
	_name = "crm.claim"
	_description = "Claim"
	_order = "priority,date desc"
	_inherit = ['mail.thread']


	@api.multi
	def _get_default_stage_id(self):
		""" Gives default stage_id """
		section_id = self._get_default_section_id()
		return self.stage_find([], section_id, [('sequence', '=', '1')])

	id = fields.Integer('ID', readonly=True)
	name = fields.Char('Claim Subject', required=True)
	active = fields.Boolean('Active', default= lambda *a: 1)
	action_next = fields.Char('Next Action')
	date_action_next = fields.Datetime('Next Action Date')
	description = fields.Text('Description')
	resolution = fields.Text('Resolution')
	create_date = fields.Datetime('Creation Date' , readonly=True)
	write_date = fields.Datetime('Update Date' , readonly=True)
	date_deadline = fields.Date('Deadline')
	date_closed = fields.Datetime('Closed', readonly=True)
	date = fields.Datetime('Claim Date', select=True, default = fields.Datetime.now)
	# ref = fields.Reference('Reference', selection=odoo.odoo.addons.base.res.res_request.referenceable_models)

	categ_id = fields.Many2one('crm.case.categ', 'Category', \
						domain="[('section_id','=',section_id),\
						('object_id.model', '=', 'crm.claim')]")
	priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority', default="1")
	type_action = fields.Selection([('correction','Corrective Action'),('prevention','Preventive Action')], 'Action Type')
	user_id = fields.Many2one('res.users', 'Responsible', track_visibility='always', default=lambda self: self.env.uid)
	user_fault = fields.Char('Trouble Responsible')
	section_id = fields.Many2one('crm.case.section', 'Sales Team', \
					select=True, help="Responsible sales team."\
							" Define Responsible user and Email account for"\
							" mail gateway.")
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('crm.case'))
	partner_id = fields.Many2one('res.partner', 'Partner')
	email_cc = fields.Text('Watchers Emails', size=252, help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma")
	email_from = fields.Char('Email', size=128, help="Destination email for email gateway.")
	partner_phone = fields.Char('Phone')
	stage_id = fields.Many2one ('crm.claim.stage', 'Stage', track_visibility='onchange',
			domain="['|', ('section_ids', '=', section_id), ('case_default', '=', True)]")
	cause = fields.Text('Root Cause')

	@api.multi
	def stage_find(self, cases, section_id, domain=[], order='sequence'):
		""" Override of the base.stage method
			Parameter of the stage search taken from the lead:
			- section_id: if set, stages must belong to this section or
			  be a default case
		"""
		if isinstance(cases, (int, long)):
			cases = self.browse(cases, context=context)
		# collect all section_ids
		section_ids = []
		if section_id:
			section_ids.append(section_id)
		for claim in cases:
			if claim.section_id:
				section_ids.append(claim.section_id.id)
		# OR all section_ids and OR with case_default
		search_domain = []
		if section_ids:
			search_domain += [('|')] * len(section_ids)
			for section_id in section_ids:
				search_domain.append(('section_ids', '=', section_id))
		search_domain.append(('case_default', '=', True))
		# AND with the domain in parameter
		search_domain += list(domain)
		# perform search, return the first found
		stage_ids = self.env['crm.claim.stage'].search(search_domain, order=order)
		if stage_ids:
			return stage_ids[0]
		return False

	@api.onchange('partner_id')
	def onchange_partner_id(self):
		"""This function returns value of partner address based on partner
		   :param email: ignored
		"""
		if not self.partner_id:
			return {'value': {'email_from': False, 'partner_phone': False}}
		address = self.partner_id
		return {'value': {'email_from': address.email, 'partner_phone': address.phone}}

	@api.model
	def create(self, vals):
		context = dict(self._context or {})
		if vals.get('section_id') and not context.get('default_section_id'):
			context['default_section_id'] = vals.get('section_id')

		# context: no_log, because subtype already handle this
		return super(CrmClaim, self).create(vals)

	@api.multi
	def copy(self, default=None):
		claim = self
		default = dict(default or {},
			# stage_id = self._get_default_stage_id(),
			name = _('%s (copy)') % claim.name)
		return super(CrmClaim, self).copy(default=default)

	# -------------------------------------------------------
	# Mail gateway
	# -------------------------------------------------------

	@api.multi
	def message_new(self, msg, custom_values=None):
		""" Overrides mail_thread message_new that is called by the mailgateway
			through message_process.
			This override updates the document according to the email.
		"""
		if custom_values is None:
			custom_values = {}
		desc = html2plaintext(msg.get('body')) if msg.get('body') else ''
		defaults = {
			'name': msg.get('subject') or _("No Subject"),
			'description': desc,
			'email_from': msg.get('from'),
			'email_cc': msg.get('cc'),
			'partner_id': msg.get('author_id', False),
		}
		if msg.get('priority'):
			defaults['priority'] = msg.get('priority')
		defaults.update(custom_values)
		return super(CrmClaim, self).message_new(msg, custom_values=defaults)

class ResPartner(models.Model):

	_inherit = 'res.partner'

	@api.multi
	def _claim_count(self):
		Claim = self.env['crm.claim']
		for partner in self:
			partner.claim_count =  Claim.search_count([('partner_id', '=', partner.id)]) 

	claim_count = fields.Integer(compute='_claim_count', string='# Claims')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: