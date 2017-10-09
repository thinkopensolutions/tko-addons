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

from openerp import models, api, fields, _
import openerp.addons.decimal_precision as dp


class pos_price_exception(models.Model):
    _name = 'pos.price.exception'

    list_price = fields.Float('Sale Price', required=True)
    config_id = fields.Many2one('pos.config', 'POS', required=True)
    template_id = fields.Many2one('product.template', 'Product', required=True, ondelete="cascade")

    _sql_constraints = [
        ('config_template_uniq', 'unique (config_id,template_id)',
         _('You can not have two prices for same product in single POS !')),
    ]


class product_template(models.Model):
    _inherit = 'product.template'

    price_exception_ids = fields.One2many('pos.price.exception', 'template_id', string='Price Exception')


class pos_config(models.Model):
    _inherit = 'pos.config'

    price_exception_ids = fields.Many2many('pos.price.exception',
                                           string='Exceptions', )  # compute='_get_price_exception_ids')

    # this method computes price exceptions for a pos
    @api.one
    def _get_price_exception_ids(self):
        self.price_exception_ids = [(6, 0, [exception.id for exception in
                                            self.env['pos.price.exception'].search([('config_id', '=', self.id)])])]


class pos_session(models.Model):
    _inherit = 'pos.session'

    price_exception_ids = fields.Many2many('pos.price.exception', 'pos_session_price_exception_rel', 'session_id',
                                           'exception_id', related='config_id.price_exception_ids', readonly=True,
                                           string='POS Price Exceptions')


class product_template(models.Model):
    _inherit = 'product.template'

    def _product_template_price(self, cr, uid, ids, name, arg, context=None):
        plobj = self.pool.get('product.pricelist')
        res = {}
        quantity = context.get('quantity') or 1.0
        pricelist = context.get('pricelist', False)
        partner = context.get('partner', False)
        if pricelist:
            # Support context pricelists specified as display_name or ID for compatibility
            if isinstance(pricelist, basestring):
                pricelist_ids = plobj.name_search(
                    cr, uid, pricelist, operator='=', context=context, limit=1)
                pricelist = pricelist_ids[0][0] if pricelist_ids else pricelist

            if isinstance(pricelist, (int, long)):
                products = self.browse(cr, uid, ids, context=context)
                qtys = map(lambda x: (x, quantity, partner), products)
                pl = plobj.browse(cr, uid, pricelist, context=context)
                price = plobj._price_get_multi(cr, uid, pl, qtys, context=context)
                for id in ids:
                    res[id] = price.get(id, 0.0)
        for id in ids:
            res.setdefault(id, 0.0)
        return res

    price_exception = fields.Char(string='Price Exception', compute='get_price_exception')

    @api.multi
    def get_price_exception(self):
        exceptions_dict = {}
        for record in self:
            for exception in record.price_exception_ids:
                exceptions_dict[exception.config_id.id] = exception.list_price
            record.price_exception = exceptions_dict
