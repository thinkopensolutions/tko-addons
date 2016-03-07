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

from openerp import models, api, fields, _

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    @api.model
    def create(self,vals):
        if 'cnpj_cpf'  in vals.keys():
            if not vals['cnpj_cpf'] or vals['cnpj_cpf'] == 'false':
                vals['cnpj_cpf'] = False
        return super(res_partner,self).create(vals)
    
    @api.multi
    def write(self,vals):
        for record in self:
            if 'cnpj_cpf'  in vals.keys():
                if not vals['cnpj_cpf'] or vals['cnpj_cpf'] == 'false':
                    vals.pop('cnpj_cpf') 
            return super(res_partner,record).write(vals)
