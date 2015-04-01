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
    
    opportunity_id = fields.Many2one('crm.lead','Opportunity')
            
    def check_fields(self, cr, uid, ids, context = None):
        for record in self.browse(cr, uid , ids):
            if not record.partner_id.is_company:
                raise osv.except_osv(_('Error'), _('selected customer should be company'))
            if not record.partner_id.legal_name:
                raise osv.except_osv(_('Error'), _('Legal Name not defined')) 
            if not record.partner_id.cnpj_cpf:
                raise osv.except_osv(_('Error'), _('CNPJ/CPF not defined'))
            if not record.partner_id.country_id:
                raise osv.except_osv(_('Error'), _("partner's country not defined"))
            if not record.partner_id.state_id:
                raise osv.except_osv(_('Error'), _("partner's state not defined"))
            if not record.partner_id.l10n_br_city_id:
                raise osv.except_osv(_('Error'), _("partner's city not defined"))
            if not record.partner_id.street:
                raise osv.except_osv(_('Error'), _("partner's street not defined"))
            if not record.partner_id.street2:
                raise osv.except_osv(_('Error'), _("partner's complement not defined"))
            if not record.partner_id.number:
                raise osv.except_osv(_('Error'), _("partner's number not defined"))
            if not record.partner_id.zip:
                raise osv.except_osv(_('Error'), _("partner's CEP not defined"))
            #main_poc_id
            if not record.partner_id.main_poc_id:
                raise osv.except_osv(_('Error'), _("partner's main contact not defined"))
            if record.partner_id.main_poc_id.is_company:
                raise osv.except_osv(_('Error'), _("partner's main contact should not be company"))
            if not record.partner_id.main_poc_id.function:
                raise osv.except_osv(_('Error'), _("partner's main contact's job not defined"))
            if not record.partner_id.main_poc_id.phone:
                raise osv.except_osv(_('Error'), _("partner's main contact's phone not defined"))
            if not record.partner_id.main_poc_id.mobile:
                raise osv.except_osv(_('Error'), _("partner's main contact's mobile not defined"))
            if not record.partner_id.main_poc_id.email:
                raise osv.except_osv(_('Error'), _("partner's main contact's email not defined"))
            
            #financial_poc_id
            if not record.partner_id.financial_poc_id:
                raise osv.except_osv(_('Error'), _("partner's financial contact not defined"))
            if record.partner_id.financial_poc_id.is_company:
                raise osv.except_osv(_('Error'), _("partner's financial contact should not be company"))
            if not record.partner_id.financial_poc_id.function:
                raise osv.except_osv(_('Error'), _("partner's financial contact's job not defined"))
            if not record.partner_id.financial_poc_id.phone:
                raise osv.except_osv(_('Error'), _("partner's financial contact's phone not defined"))
            if not record.partner_id.financial_poc_id.mobile:
                raise osv.except_osv(_('Error'), _("partner's financial contact's mobile not defined"))
            if not record.partner_id.financial_poc_id.email:
                raise osv.except_osv(_('Error'), _("partner's financial contact's email not defined"))
            
            
            #project_poc_id
            if not record.partner_id.project_poc_id:
                raise osv.except_osv(_('Error'), _("partner's project contact not defined"))
            if record.partner_id.project_poc_id.is_company:
                raise osv.except_osv(_('Error'), _("partner's project contact should not be company"))
            if not record.partner_id.project_poc_id.function:
                raise osv.except_osv(_('Error'), _("partner's project contact's job not defined"))
            if not record.partner_id.project_poc_id.phone:
                raise osv.except_osv(_('Error'), _("partner's project contact's phone not defined"))
            if not record.partner_id.project_poc_id.mobile:
                raise osv.except_osv(_('Error'), _("partner's project contact's mobile not defined"))
            if not record.partner_id.project_poc_id.email:
                raise osv.except_osv(_('Error'), _("partner's project contact's email not defined"))
            
            #opportunity
            if not record.opportunity_id:
                raise osv.except_osv(_('Error'), _("sale order not defined"))
            #if not record.opportunity_id.cpps_description:
            #    raise osv.except_osv(_('Error'), _("opportunity's description not defined"))
            if not record.opportunity_id.service_type:
                raise osv.except_osv(_('Error'), _("opportunity's service type not defined"))
            if not record.opportunity_id.sla:
                raise osv.except_osv(_('Error'), _("opportunity's sla type not defined"))
            if not record.opportunity_id.maintenance_window:
                raise osv.except_osv(_('Error'), _("opportunity's maintenance window not defined"))
            if not record.opportunity_id.support_ticket:
                raise osv.except_osv(_('Error'), _("opportunity's support ticket not defined"))
            
            if not record.opportunity_id.database_size:
                raise osv.except_osv(_('Error'), _("database size not defined"))
            if not record.opportunity_id.number_users:
                raise osv.except_osv(_('Error'), _("no of users not defined"))
            if not record.opportunity_id.backups_policy:
                raise osv.except_osv(_('Error'), _("backup policy not defined"))
            if not record.opportunity_id.migrations_policy:
                raise osv.except_osv(_('Error'), _("migration policy not defined"))
            if not record.opportunity_id.support_maintenance:
                raise osv.except_osv(_('Error'), _("Support & Maintenance not defined"))
            if not record.opportunity_id.notes:
                raise osv.except_osv(_('Error'), _("opportunity's notes not defined"))
            
            
            if not record.opportunity_id.implementation_value:
                raise osv.except_osv(_('Error'), _("Implementation Value not defined"))
            if not record.opportunity_id.support_value:
                raise osv.except_osv(_('Error'), _("Support Value not defined"))
            if not record.opportunity_id.recurring_invoicing:
                raise osv.except_osv(_('Error'), _("Recurring Invoicing not defined"))
            if not record.opportunity_id.discount_validity:
                raise osv.except_osv(_('Error'), _("Discount Validity not defined"))
            if not record.opportunity_id.payment_description:
                raise osv.except_osv(_('Error'), _("Payment Terms not defined"))
            if not record.opportunity_id.module_ids:
                raise osv.except_osv(_('Error'), _("Modules not defined"))
            if not record.opportunity_id.fidelidade:
                raise osv.except_osv(_('Error'), _("fidelidade not defined"))
            if not record.opportunity_id.duration:
                raise osv.except_osv(_('Error'), _("duration not defined"))
            if not record.opportunity_id.updates:
                raise osv.except_osv(_('Error'), _("updates not defined"))
            
    
        return True
    
    def generate_contract(self, cr, uid, ids, context=None):
         self._check_fields(cr, uid, ids, context = context)
         res = super(account_analytic_account, self).generate_contract(cr, uid, ids, context = context)
         return res
     
     
     
