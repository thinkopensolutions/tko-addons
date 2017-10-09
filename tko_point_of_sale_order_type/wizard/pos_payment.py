# -*-coding:utf-8-*-
from openerp import models, fields, api
from ..point_of_sale import pos_order_types


class pos_make_payment(models.TransientModel):
    _inherit = 'pos.make.payment'

    order_type = fields.Selection(string='Order Type',
                                  selection=pos_order_types,
                                  default='t',
                                  required=True, )

    @api.one
    def check(self):
        pos_order = self.env['pos.order'].browse(self.env.context.get('active_id', False))
        pos_order.order_type = self.order_type
        return super(pos_make_payment, self).check()
