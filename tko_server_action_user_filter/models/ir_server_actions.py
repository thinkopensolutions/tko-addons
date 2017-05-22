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

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
import time
import logging
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    filter_id = fields.Many2one('ir.filters', 'Filter',
                                help='If the domain is set, Server action will run only if domain is satisfied')
    model = fields.Char(related='model_id.model', string='Model')
    validate_filter_obj = fields.Boolean("Filter Object", compute='validate_filter_object')
    field_id = fields.Many2one('ir.model.fields', 'Fields')

    @api.constrains('model_id', 'field_id')
    def validate_field(self):
        """
        Checks if a class has the selected field
        """
        for record in self:
            found = False
            for field in record.model_id.field_id:
                if field.ttype == 'many2one' and field.name == record.field_id.name:
                    found = True
                    break
            if not found:
                raise Warning(u"Model %s has no field %s" % (record.model_id.name, record.field_id.field_description))
        return True

    # return True if object is same
    @api.one
    @api.depends('filter_id')
    def validate_filter_object(self):
        if not self.filter_id or (self.filter_id and self.model == self.filter_id.model_id):
            self.validate_filter_obj = True
        else:
            self.validate_filter_obj = False

    @api.model
    def _eval_context(self):
        """Returns a dictionary to use as evaluation context for
           ir.rule domains."""
        return {'user': self.env.user, 'time': time}

    # Method 2
    def validate_server_action(self):
        """

        Context must have active_id
        :return:
        """
        model_name = self.model_id.model
        eval_context = self._eval_context()
        active_id = self._context.get('active_id', False)
        if not self.validate_filter_obj and self.field_id:
            original_model = model_name
            model_name = self.field_id.relation
            field_name = self.field_id.name
            object = self.env[original_model].browse(active_id)
            record = getattr(object, field_name)

            if not record.id:
                _logger.error("Field %s not set, server action not executed" % self.field_id.field_description)
                return False
            active_id = record.id
        if active_id and model_name:
            domain = self.filter_id.domain
            rule = expression.normalize_domain(safe_eval(domain, eval_context))
            Query = self.env[model_name].sudo()._where_calc(rule, active_test=False)
            from_clause, where_clause, where_clause_params = Query.get_sql()
            where_str = where_clause and (" WHERE %s" % where_clause) or ''
            query_str = 'SELECT id FROM ' + from_clause + where_str
            self._cr.execute(query_str, where_clause_params)
            result = self._cr.fetchall()
            if active_id in [id[0] for id in result]:
                return True
        else:
            _logger.error("Server Action was called without 'active_id' not executed")
        return False

    # if filter is set, execute server action only if condition is satisfied
    @api.multi
    def run(self):
        if self.filter_id.domain:
            result = self.validate_server_action()
            if not result:
                return False
        return super(IrActionsServer, self).run()



        # # Method 1 commented because we are using Method2
        # def validate_server_action(self):
        #     """
        #
        #     Context must have active_id
        #     :return:
        #     """
        #     eval_context = self._eval_context()
        #     active_id = self._context.get('active_id', False)
        #     active_id = 29
        #     object = self.env[self.model_id.model].browse(active_id)
        #     domain = self.filter_id.domain
        #     rule = expression.normalize_domain(safe_eval(domain, eval_context))
        #
        #     domain_result = self.normalize(object, rule)
        #     result = self.validate_domain(domain_result)
        #     return result
        #
        #
        # def normalize(self, object, rule):
        #     user = self.env.user
        #     from odoo.http import request
        #     Model = request.env[self.model_id.model]
        #     if rule:
        #         for tup in rule:
        #             index = rule.index(tup)
        #             if isinstance(tup, tuple) or isinstance(tup, list):
        #                 left_conditon = tup[0]
        #                 value = object
        #                 for field_name in left_conditon.split('.'):
        #                     if field_name == 'user':
        #                         value = user
        #                     elif field_name == 'time':
        #                         value = time
        #                     else:
        #                         try:
        #                             value = value[field_name]
        #                             field_type = Model.fields_get( allfields=[field_name])[field_name]['type']
        #                             value_bkp = value
        #                             if field_type == 'many2one':
        #                                 value = value.id
        #                         except:
        #                             raise Warning(_("Field %s doesn't exist" % (field_name)))
        #                     rule[index] = (value, tup[1], tup[2])
        #                     value = value_bkp
        #
        #     return rule
        #
        #
        #
        # # this method converts operator string in pythonic operator
        #
        # def compute_tuple(self, tup):
        #     if tup:
        #         operator = tup[1]
        #         tup_zero = tup[0]
        #         tup_two = tup[2]
        #         if tup_zero == '':
        #             tup_zero = False
        #
        #         if tup_two == '':
        #             tup_two = False
        #
        #         if operator == '=':
        #             result = tup_zero == tup_two
        #
        #         elif operator == '!=' or operator == '<>':
        #             result = tup_zero != tup_two
        #
        #         elif operator == 'in':
        #             result = tup_zero in tup_two
        #
        #         elif operator == 'or' or operator == '||':
        #             result = tup_zero or tup_two
        #
        #         elif operator == 'and' or operator == '&&':
        #             result = tup_zero and tup_two
        #
        #         elif operator == 'not in':
        #             result = tup_zero not in tup_two
        #
        #         elif operator == 'like':
        #             result = tup_zero in tup_two
        #
        #         elif operator == '<':
        #             result = float(tup_zero) < float(tup_two)
        #
        #         elif operator == '>':
        #             result = float(tup_zero) > float(tup_two)
        #
        #         elif operator == '>=':
        #             result = float(tup_zero) >= float(tup_two)
        #
        #         elif operator == '<=':
        #             result = float(tup_zero) <= float(tup_two)
        #
        #         elif operator == 'ilike':
        #             result = str(tup_zero).lower() in str(tup_two).lower()
        #         else:
        #             raise Warning(_("Unsupported domain %s") % operator)
        #
        #         return result
        #
        # def validate_domain(self, domain):
        #     if domain:
        #         if not isinstance(domain, list):
        #             raise Warning(_('Domain must be list'))
        #         # if it is single domain compute and return result
        #         if isinstance(domain, list) and len(domain) == 1:
        #             result = self.compute_tuple(domain[0])
        #             return result
        #         # domain is always a list
        #         if isinstance(domain, list) and len(domain) >= 3:
        #             pos_and = pos_or = False
        #             if '&' in domain:
        #                 pos_and = -domain[::-1].index('&') - 1
        #             if '|' in domain:
        #                 pos_or = -domain[::-1].index('|') - 1
        #             # compute most right operator and its index
        #             if pos_and and pos_or:
        #                 if pos_and > pos_or:
        #                     pos = pos_and
        #                     operator = 'and'
        #                 else:
        #                     pos = pos_or
        #                     operator = 'or'
        #             elif pos_and:
        #                 pos = pos_and
        #                 operator = 'and'
        #
        #             elif pos_or:
        #                 pos = pos_or
        #                 operator = 'or'
        #
        #             # replace tuples with True or False
        #             if isinstance(domain[pos + 1], tuple):
        #                 result = self.compute_tuple(domain[pos + 1])
        #                 domain[pos + 1] = result
        #
        #             if isinstance(domain[pos + 2], tuple):
        #                 result = self.compute_tuple(domain[pos + 2])
        #                 domain[pos + 2] = result
        #             if operator == 'and':
        #                 new_value = domain[pos + 1] and domain[pos + 2]
        #             if operator == 'or':
        #                 new_value = domain[pos + 1] or domain[pos + 2]
        #
        #             domain.remove(domain[pos])
        #             domain.remove(domain[pos + 1])
        #             domain.remove(domain[pos + 2])
        #             domain.append(new_value)
        #
        #             if len(domain) >= 2:
        #                 self.validate_domain(domain)
        #     return domain[0]
