# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
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

from datetime import datetime, timedelta

from openerp.osv import osv, fields


class survey_user_input(osv.Model):
    _inherit = "survey.user_input"
    _rec_name = "date_write"

    def _get_claim_id(self, cr, uid, ids, name, unknown, context=None):
        res = {}
        for record in self.browse(cr, uid, ids):
            if record.partner_id and record.survey_id:
                claim_id = self.pool.get('crm.claim').search(cr, uid, [('survey_ans_id', '=', record.id)],
                                                             order='id desc')
                if len(claim_id):
                    res[record.id] = claim_id[0]
        return res

    _columns = {
        'claim_id': fields.function(_get_claim_id, type="many2one", relation='crm.claim', string='Claim', ),
        'date_write': fields.datetime('Write Date'),
    }
    _defaults = {
        'date_write': lambda *a: datetime.now()
    }

    def write(self, cr, uid, ids, vals, context=None):
        date_time = datetime.now() - timedelta(hours=3)
        vals.update({'date_write': str(date_time)[0:19]})
        return super(survey_user_input, self).write(cr, uid, ids, vals, context=context)


class survey_mail_compose_message(osv.TransientModel):
    _inherit = 'survey.mail.compose.message'

    def default_get(self, cr, uid, fields, context=None):
        res = super(survey_mail_compose_message, self).default_get(cr, uid, fields, context=context)
        if context.get('active_model') == 'crm.claim' and context.get('active_ids'):
            claim_obj = self.pool.get('crm.claim').browse(cr, uid, context.get('active_id'))
            survey_id = claim_obj.survey_id.id
            template = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'survey', 'email_template_survey')
            if template:
                res.update({'template_id': template[1]})
            res.update({'survey_id': survey_id, 'partner_ids': [(6, 0, [part.id for part in claim_obj.partner_id])]})
        return res

    def send_mail(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', [])
        active_model = context.get('active.model', False)

        if active_ids and active_model == 'crm.claim':
            self.pool.get('crm.claim').write(cr, uid, active_ids, {
                'partner_id': [partner.id for partner in self.browse(cr, uid, ids[0]).partner_ids][0]})
        return super(survey_mail_compose_message, self).send_mail(cr, uid, ids, context=context)
