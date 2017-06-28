# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import fields, osv

class stock_move(osv.osv):
    _name = "tko.stock.move"
    _inherit = "stock.move"
    _description = "Stock Move Transactions"

    _columns = {
        'move_type': fields.many2one('tko.stock.move.move_type_id', 'Move Type', required=True, select=True,
                                      states={'done': [('readonly', True)]}),
        'move_type_id': fields.selection([('in', 'In'),
                                          ('out', 'Out')
                                         ], 'Move Type', readonly=True, select=True, copy=False,
                                         help="In: For product quantities entering stock.\n" \
                                              "Out: For product quantities leaving stock.")
    }

    #def