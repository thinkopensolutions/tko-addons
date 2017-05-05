# -*- encoding: utf-8 -*-
# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    nickname = fields.Char('Nickname')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.nickname and "[" + record.nickname + "] " + record.name or record.name
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args.insert(0, ['name', operator, name])
        args.insert(0, ['nickname', operator, name])
        args.insert(0, '|')
        res = super(ResPartner, self).name_search(name, args=args, operator=operator, limit=limit)
        return res
