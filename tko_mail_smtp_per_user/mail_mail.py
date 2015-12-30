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


class ir_mail_server(osv.osv):
    _inherit = 'ir.mail_server'

    _columns = {
        'user_id': fields.many2one('res.users', string='Owner'),
    }

    _sql_constraints = [
        ('smtp_user_uniq',
         'unique(user_id)',
         'That user already has a SMTP server.'),
    ]


class mail_mail(osv.Model):
    _inherit = 'mail.mail'

    def send(
            self,
            cr,
            uid,
            ids,
            auto_commit=False,
            raise_exception=False,
            context=None):
        ir_mail_server = self.pool.get('ir.mail_server')
        res_users = self.pool.get('res.users')
        email_ids = self.pool.get('mail.mail').browse(
            cr, uid, ids, context=context)
        for email in email_ids:
            user_id = res_users.search(
                cr, uid, [
                    ('partner_id', '=', email.author_id.id)], context=context)
            user_id = user_id and user_id[0] or False
            if user_id:
                server_id = ir_mail_server.search(
                    cr, uid, [('user_id', '=', user_id)], context=context)
                server_id = server_id and server_id[0] or False
                if server_id:
                    self.write(
                        cr, uid, ids, {
                            'mail_server_id': server_id, 'reply_to': email.email_from}, context=context)
        return super(
            mail_mail,
            self).send(
            cr,
            uid,
            ids,
            auto_commit=auto_commit,
            raise_exception=raise_exception,
            context=context)
