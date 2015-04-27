# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen - Portugal & Brasil
#    Copyright (C) Thinkopen Solutions (<http://www.thinkopensolutions.com>).
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

from openerp import models, api, fields, _
from openerp.osv import osv


class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    date_contract_sent = fields.Datetime('Contract Sent',
                              track_visibility='onchange')
    contract_template_body_id = fields.Many2one('account.analytic.account.contract.report.body',
                              track_visibility='onchange', string=u'Contract')
    state = fields.Selection([('template', 'Template'),
                               ('draft', 'New'),
                               ('sent', 'Contract Sent'),
                               ('open', 'In Progress / Signed'),
                               ('pending', 'To Renew'),
                               ('close', 'Closed'),
                               ('cancelled', 'Cancelled'),
                               ],
                              'Status', required=True,
                              track_visibility='onchange', copy=False)

    _defaults = {
        'state': 'draft',
    }
    
    def generate_contract(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        
        datas = {
            'ids': context.get('active_ids', []),
            'model': 'account.analytic.account',
            'form': data
        }
        
        datas['form']['active_ids'] = context.get('active_ids', False)
        
        return self.pool['report'].get_action(cr, uid, [], 'tko_account_contract_report_template.tko_contract_report', data=datas, context=context)
    
    def action_contract_sent(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi invoice template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        contract_obj = self.browse(cr, uid, ids[0])
        attach_obj = self.pool.get('ir.attachment')
        contract_name = contract_obj.name + '-contract.pdf'
        
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'tko_account_contract_report_template', 'email_template_contract')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'account.analytic.account',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_invoice_as_sent': True,
            })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        
    def check_fields(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid , ids):
            # CHECK PARTNER, COMPANY FIELDS
            if not record.company_id:
                raise osv.except_osv(_('Error'), _('Company not defined'))
            if not record.company_id.phone:
                raise osv.except_osv(_('Error'), _("Company's phone not defined"))
            if not record.company_id.country_id:
                raise osv.except_osv(_('Error'), _("Company's country not defined"))
            if not record.company_id.state_id:
                raise osv.except_osv(_('Error'), _("Company's state not defined"))
            if not record.company_id.city:
                raise osv.except_osv(_('Error'), _("Company's city not defined"))
            if not record.company_id.street:
                raise osv.except_osv(_('Error'), _("Company's street not defined"))
            if not record.company_id.street2:
                raise osv.except_osv(_('Error'), _("Company's complement not defined"))
            if not record.company_id.zip:
                raise osv.except_osv(_('Error'), _("Company's zip not defined"))
            
            # CHECK PARTNER, CLIENT FIELDS
            if not record.partner_id:
                raise osv.except_osv(_('Error'), _('Customer not defined'))
            if not record.partner_id.phone:
                raise osv.except_osv(_('Error'), _("Customer's phone not defined"))
            if not record.partner_id.mobile:
                raise osv.except_osv(_('Error'), _("Customer's mobile not defined"))
            if not record.partner_id.email:
                raise osv.except_osv(_('Error'), _("Customer's email not defined"))
            if not record.partner_id.country_id:
                raise osv.except_osv(_('Error'), _("Customer's country not defined"))
            if not record.partner_id.state_id:
                raise osv.except_osv(_('Error'), _("Customer's state not defined"))
            if not record.partner_id.city:
                raise osv.except_osv(_('Error'), _("Customer's city not defined"))
            if not record.partner_id.street:
                raise osv.except_osv(_('Error'), _("Customer's street not defined"))
            if not record.partner_id.street2:
                raise osv.except_osv(_('Error'), _("Customer's complement not defined"))
            if not record.partner_id.zip:
                raise osv.except_osv(_('Error'), _("Customer's zip not defined"))
            
            # CHECK PARTNER, ACCOUNT MANAGER FIELDS
            if not record.manager_id:
                raise osv.except_osv(_('Error'), _('Account Manager not defined'))
            if not record.manager_id.phone:
                raise osv.except_osv(_('Error'), _("Account Manager's phone not defined"))
            if not record.manager_id.mobile:
                raise osv.except_osv(_('Error'), _("Account Manager's mobile not defined"))
            if not record.manager_id.email:
                raise osv.except_osv(_('Error'), _("Account Manager's email not defined"))
            if not record.manager_id.country_id:
                raise osv.except_osv(_('Error'), _("Account Manager's country not defined"))
            if not record.manager_id.state_id:
                raise osv.except_osv(_('Error'), _("Account Manager's state not defined"))
            if not record.manager_id.city:
                raise osv.except_osv(_('Error'), _("Account Manager's city not defined"))
            if not record.manager_id.street:
                raise osv.except_osv(_('Error'), _("Account Manager's street not defined"))
            if not record.manager_id.street2:
                raise osv.except_osv(_('Error'), _("Account Manager's complement not defined"))
            if not record.manager_id.zip:
                raise osv.except_osv(_('Error'), _("Account Manager's zip not defined"))
            if not record.manager_id.function:
                raise osv.except_osv(_('Error'), _("Account Manager's function not defined"))
            return True
    
    
class account_analytic_account_contract_report_body(models.Model):
    _name = 'account.analytic.account.contract.report.body'
    _inherit = 'mail.thread'
    
    name = fields.Char(string='Name',
                   track_visibility='onchange', required=True)
    signature = fields.Binary(string='Signature',
                   track_visibility='onchange', required=True)
    contract_body = fields.Text(string='Contract Body',
                   track_visibility='onchange', required=True,
                   translate=True)
    
