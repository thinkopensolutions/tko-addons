# -*-coding:utf-8-*-
from openerp import models, fields

pos_order_types = [('v', 'Venda'), ('t', 'Troca'), ('c', 'Cancelamento')]


class pos_order(models.Model):
    _inherit = 'pos.order'

    order_type = fields.Selection(string="Order Type",
                                  selection=pos_order_types,
                                  default='v',
                                  required=False, )
