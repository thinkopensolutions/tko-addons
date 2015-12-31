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

from openerp.osv import osv, fields
from openerp import api
from openerp import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


class res_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"
    _description = "inherited partner class"

    def create(self, cr, uid, vals, context=False):
        mail_obj = self.pool.get('res.partner.email')
        res = super(res_partner, self).create(cr, uid, vals, context=context)
        email_ids = mail_obj.search(cr, uid, [('res_partner_id', '=', res)])
        if email_ids:
            mail_obj.write(cr, uid, email_ids[0], {'is_active': True})
            vals.update({'email': mail_obj.browse(
                cr, uid, email_ids[0]).email})
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(
            res_partner,
            self).write(
            cr,
            uid,
            ids,
            vals,
            context=context)
        email_ids = []
        if isinstance(ids, int):
            ids = [ids]
        mail_obj = self.pool.get('res.partner.email')
        if len(ids):
            email_ids = mail_obj.search(
                cr, uid, [('res_partner_id', '=', ids[0])])
            if len(email_ids) == 1:
                mail_obj.write(cr, uid, email_ids[0], {'is_active': True})
        return res

    def _get_email_id(self, cr, uid, ids, name, args, context=False):
        res = {}
        email_obj = self.pool.get('res.partner.email')
        for record in self.browse(cr, uid, ids):
            email_ids = email_obj.search(
                cr, uid, [
                    ('res_partner_id', '=', record.id), ('is_active', '=', True)])
            if email_ids:
                email = email_obj.browse(cr, uid, email_ids[0]).email
                res[record.id] = email
            else:
                res[record.id] = False
        return res

    def _set_email_id(self, cr, uid, ids, name, value, args, context=None):
        mail_obj = self.pool.get('res.partner.email')
        if value and ids:
            for record in self.browse(cr, uid, ids):
                mail_ids = mail_obj.search(
                    cr, uid, [
                        ('res_partner_id', '=', record.id), ('email', 'ilike', value)])
                if mail_ids:
                    previous_mail_ids = mail_obj.search(
                        cr, uid, [('res_partner_id', '=', record.id)])
                    mail_obj.write(
                        cr, uid, previous_mail_ids, {
                            'is_active': False})
                    mail_obj.write(cr, uid, mail_ids, {'is_active': True})
                if not mail_ids:
                    active_mail_ids = mail_obj.search(
                        cr, uid, [('res_partner_id', '=', record.id), ('is_active', '=', True)])
                    if len(active_mail_ids):
                        mail_obj.write(
                            cr, uid, active_mail_ids, {
                                'email': value})
                    else:
                        # mail_obj.write(cr, uid, previous_mail_ids, {'is_active' : False})
                        mail_obj.create(cr, uid, {'res_partner_id': record.id,
                                                  'email': value,
                                                  'is_active': True})
        if not value:
            for record in self.browse(cr, uid, ids):
                mail_id = mail_obj.search(
                    cr, uid, [
                        ('res_partner_id', '=', record.id), ('is_active', '=', True)])
                if len(mail_id):
                    mail_obj.unlink(cr, uid, mail_id)
        return True

    def _get_partner(self, cr, uid, ids, context=None):
        result = {}
        for part in self.pool.get('res.partner.email').browse(
                cr, uid, ids, context=context):
            result[part.res_partner_id.id] = True
        return result.keys()

    def _get_mail_ids(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for mail in ids:
            res[mail] = self.pool.get('res.partner.email').search(
                cr, uid, [('res_partner_id', '=', mail)])
        return res

    _columns = {
        'email': fields.function(
            _get_email_id, type='char', fnct_inv=_set_email_id, string='Email', store={
                'res.partner': (
                    lambda self, cr, uid, ids, c={}: ids, ['email_ids'], 10), 'res.partner.email': (
                    _get_partner, [
                        'email', 'is_active'], 10), }), 'email_ids': fields.one2many(
                            'res.partner.email', 'res_partner_id', 'Emails'), 'email_ids_readonly': fields.function(
                                _get_mail_ids, type='one2many', relation='res.partner.email', string='Emails')}

    def _create_multiple_emails_at_first_install(
            self, cr, SUPERUSER_ID, ids=None, context=None):
        partner_ids = self.search(cr, SUPERUSER_ID, [('email', '!=', False)])
        part_email_obj = self.pool.get('res.partner.email')
        for partner_id in partner_ids:
            _logger.info(
                "Setting up multiple email '%s' record for client %s ." %
                (partner.email, partner.name))
            partner = self.browse(cr, SUPERUSER_ID, partner_id)
            try:
                part_email_obj.create(cr, SUPERUSER_ID, {
                    'email': partner.email,
                    'is_active': True,
                    'res_partner_id': partner_id,
                })
            except:
                _logger.warning(
                    "Unable to setup multiple email '%s' record for client %s ." %
                    (partner.email, partner.name))
        return True
