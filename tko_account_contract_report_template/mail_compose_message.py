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

from openerp.osv import osv
from datetime import datetime

class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'
    
    def send_mail(self, cr, uid, ids, context=None):
        res = super(mail_compose_message, self).send_mail(cr, uid, ids, context=context)
        active_model = context.get('active_model' , False)
        if active_model == 'account.analytic.account':
            active_ids = context.get('active_ids', [])
            if active_ids:
                self.pool.get('account.analytic.account').write(cr, uid, active_ids, {'state' : 'sent', 'date_contract_sent' : datetime.now()}, context=context)
        return res
