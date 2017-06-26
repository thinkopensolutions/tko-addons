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



from odoo import fields, models, api, _

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    phone_ids = fields.One2many('phone.number', 'partner_id', string=u'Phones')
    # phone_ids_readonly = fields.function('_get_phone_ids', type='one2many', relation='.partner.phone', string='Phones')
    # phone = fields.Char('_get_phones', fnct_inv='_set_phone_id', type='char', multi="phones", string='Phone',
    #                     store={'.partner': (lambda self, cr, uid, ids, c={}: ids, ['phone_ids'], 10),
    #                            '.partner.phone': ('_get_partner', ['type', 'phone', 'is_active'], 10), }
    #
    #                     )
    #
    # mobile = fields.Char('_get_phones', fnct_inv='_set_mobile_id', type='char', multi="phones", string='Mobile',
    #                      store={'.partner': (lambda self, cr, uid, ids, c={}: ids, ['phone_ids'], 10),
    #                             '.partner.phone': ('_get_partner', ['type', 'phone', 'is_active'], 10), }
    #
    #                      )


    # def create(self, cr, uid, vals, context=False):
    #     phone_obj = self.pool.get('.partner.phone')
    #     phone_type_id = self.pool.get('.partner.phone.type').search(
    #         cr, uid, [('code', '=', 'phone')])
    #     mobile_type_id = self.pool.get('.partner.phone.type').search(
    #         cr, uid, [('code', '=', 'cel')])
    #      = super(_partner, self).create(cr, uid, vals, context=context)
    #     phone_ids = phone_obj.search(
    #         cr, uid, [
    #             ('_partner_id', '=', ), ('type_id', '=', phone_type_id[0])])
    #     mobile_ids = phone_obj.search(
    #         cr, uid, [('_partner_id', '=', ), ('type_id', '=', mobile_type_id[0])])
    #     if phone_ids:
    #         phone_obj.write(cr, uid, phone_ids[0], {'is_active': True})
    #     if mobile_ids:
    #         phone_obj.write(cr, uid, mobile_ids[0], {'is_active': True})
    #     return
    #
    # def write(self, cr, uid, ids, vals, context=False):
    #      = super(
    #         _partner,
    #         self).write(
    #         cr,
    #         uid,
    #         ids,
    #         vals,
    #         context=context)
    #     if isinstance(ids, int):
    #         ids = [ids]
    #     if len(ids):
    #         ids = ids[0]
    #         phone_obj = self.pool.get('.partner.phone')
    #         phone_type_id = self.pool.get('.partner.phone.type').search(
    #             cr, uid, [('code', '=', 'phone')])
    #         mobile_type_id = self.pool.get('.partner.phone.type').search(
    #             cr, uid, [('code', '=', 'cel')])
    #         phone_ids = phone_obj.search(
    #             cr, uid, [
    #                 ('_partner_id', '=', ids), ('type_id', '=', phone_type_id[0])])
    #         mobile_ids = phone_obj.search(
    #             cr, uid, [
    #                 ('_partner_id', '=', ids), ('type_id', '=', mobile_type_id[0])])
    #         if len(phone_ids) == 1:
    #             phone_obj.write(cr, uid, phone_ids, {'is_active': True})
    #         if len(mobile_ids) == 1:
    #             phone_obj.write(cr, uid, mobile_ids, {'is_active': True})
    #     return
    #
    # def _get_phones(self, cr, uid, ids, name, args, context=False):
    #      = {}
    #     phone_obj = self.pool.get('.partner.phone')
    #     for record in self.browse(cr, uid, ids):
    #         [record.id] = {'phone': False, 'mobile': False}
    #         phone_type_id = self.pool.get('.partner.phone.type').search(
    #             cr, uid, [('code', '=', 'phone')])
    #         mobile_type_id = self.pool.get('.partner.phone.type').search(
    #             cr, uid, [('code', '=', 'cel')])
    #         phone_ids = []
    #         mobile_ids = []
    #         if phone_type_id:
    #             phone_ids = phone_obj.search(cr,
    #                                          uid,
    #                                          [('_partner_id',
    #                                            '=',
    #                                            record.id),
    #                                           ('type_id',
    #                                            '=',
    #                                            phone_type_id[0]),
    #                                           ('is_active',
    #                                            '=',
    #                                            True)],
    #                                          order='id desc',
    #                                          limit=1,
    #                                          )
    #         if mobile_type_id:
    #             mobile_ids = phone_obj.search(cr,
    #                                           uid,
    #                                           [('_partner_id',
    #                                             '=',
    #                                             record.id),
    #                                            ('type_id',
    #                                             '=',
    #                                             mobile_type_id[0]),
    #                                            ('is_active',
    #                                             '=',
    #                                             True)],
    #                                           order='id desc',
    #                                           limit=1,
    #                                           )
    #         if len(phone_ids):
    #             [record.id]['phone'] = phone_obj.browse(
    #                 cr, uid, phone_ids[0]).phone
    #         if len(mobile_ids):
    #             [record.id]['mobile'] = phone_obj.browse(
    #                 cr, uid, mobile_ids[0]).phone
    #     return
    #
    # def _set_phone_id(self, cr, uid, ids, name, value, args, context=None):
    #     phone_obj = self.pool.get('.partner.phone')
    #     for record in self.browse(cr, uid, ids):
    #         if value and ids:
    #             for record in self.browse(cr, uid, ids):
    #                 phone_type_id = self.pool.get('.partner.phone.type').search(
    #                     cr, uid, [('code', '=', 'phone')])
    #                 phone_ids = phone_obj.search(
    #                     cr, uid, [
    #                         ('_partner_id', '=', record.id), ('phone', '=', value),
    #                         ('type_id', '=', phone_type_id[0])])
    #
    #             if phone_ids:
    #                 previous_phone_ids = phone_obj.search(
    #                     cr, uid, [
    #                         ('_partner_id', '=', record.id), ('type_id', '=', phone_type_id[0])])
    #                 phone_obj.write(
    #                     cr, uid, previous_phone_ids, {
    #                         'is_active': False})
    #                 phone_obj.write(cr, uid, phone_ids, {'is_active': True})
    #
    #             if not phone_ids:
    #                 previous_phone_ids = phone_obj.search(
    #                     cr, uid, [
    #                         ('_partner_id', '=', record.id), ('type_id', '=', phone_type_id[0])])
    #                 phone_obj.write(
    #                     cr, uid, previous_phone_ids, {
    #                         'is_active': False})
    #                 phone_obj.create(cr, uid, {'_partner_id': record.id,
    #                                            'phone': value,
    #                                            'is_active': True,
    #                                            'type_id': phone_type_id[0]})
    #     return True
    #
    # def _set_mobile_id(self, cr, uid, ids, name, value, args, context=None):
    #     phone_obj = self.pool.get('.partner.phone')
    #     for record in self.browse(cr, uid, ids):
    #         if value and ids:
    #             for record in self.browse(cr, uid, ids):
    #                 phone_type_id = self.pool.get('.partner.phone.type').search(
    #                     cr, uid, [('code', '=', 'cel')])
    #                 phone_ids = phone_obj.search(
    #                     cr, uid, [
    #                         ('_partner_id', '=', record.id), ('phone', '=', value),
    #                         ('type_id', '=', phone_type_id[0])])
    #
    #             if phone_ids:
    #                 previous_phone_ids = phone_obj.search(
    #                     cr, uid, [
    #                         ('_partner_id', '=', record.id), ('type_id', '=', phone_type_id[0])])
    #                 phone_obj.write(
    #                     cr, uid, previous_phone_ids, {
    #                         'is_active': False})
    #                 phone_obj.write(cr, uid, phone_ids, {'is_active': True})
    #
    #             if not phone_ids:
    #                 previous_phone_ids = phone_obj.search(
    #                     cr, uid, [
    #                         ('_partner_id', '=', record.id), ('type_id', '=', phone_type_id[0])])
    #                 phone_obj.write(
    #                     cr, uid, previous_phone_ids, {
    #                         'is_active': False})
    #                 phone_obj.create(cr, uid, {'_partner_id': record.id,
    #                                            'phone': value,
    #                                            'is_active': True,
    #                                            'type_id': phone_type_id[0]})
    #     return True
    #
    # def _get_partner(self, cr, uid, ids, context=None):
    #     ult = {}
    #     for part in self.pool.get('.partner.phone').browse(
    #             cr, uid, ids, context=context):
    #         ult[part._partner_id.id] = True
    #     return ult.keys()
    #
    # def _get_phone_ids(self, cr, uid, ids, fields, arg, context=None):
    #      = {}
    #     for phone in ids:
    #         [phone] = self.pool.get('.partner.phone').search(
    #             cr, uid, [('_partner_id', '=', phone)])
    #     return



    # def _create_multiple_phones_at_first_install(
    #         self, cr, SUPERUSER_ID, ids=None, context=None):
    #     partner_ids = self.search(
    #         cr, SUPERUSER_ID, [
    #             '|', ('phone', '!=', False), ('mobile', '!=', False)])
    #     part_phone_obj = self.pool.get('.partner.phone')
    #
    #     cel = self.pool.get('.partner.phone.type').search(
    #         cr, SUPERUSER_ID, [('code', '=', 'cel')])[0]
    #     phone = self.pool.get('.partner.phone.type').search(
    #         cr, SUPERUSER_ID, [('code', '=', 'phone')])[0]
    #
    #     for partner_id in partner_ids:
    #         partner = self.browse(cr, SUPERUSER_ID, partner_id)
    #         phone_number = partner.phone
    #         mobile_number = partner.mobile
    #         _logger.info(
    #             'Setting up multiple phones record for client %s .' %
    #             partner.name)
    #
    #         if phone_number:
    #             part_phone_obj.create(cr, SUPERUSER_ID, {
    #                 'phone': phone_number,
    #                 'is_active': True,
    #                 '_partner_id': partner_id,
    #                 'type_id': phone
    #             })
    #             _logger.info('Set multiple phone %s for client %s' %(phone_number, partner.name))
    #         if mobile_number:
    #             part_phone_obj.create(cr, SUPERUSER_ID, {
    #                 'phone': mobile_number,
    #                 'is_active': True,
    #                 '_partner_id': partner_id,
    #                 'type_id': cel
    #             })
    #             _logger.info('Set multiple mobile %s for client %s' %(mobile_number, partner.name))
    #     return True
