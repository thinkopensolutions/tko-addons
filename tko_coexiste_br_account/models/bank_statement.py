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

import json
from openerp import models, fields, api, _
import datetime
from odoo.exceptions import Warning as UserError
from odoo.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"


    # update name in move lines if product_id is set
    @api.multi
    def process_reconciliations(self, data):
        """ Handles data sent from the bank statement reconciliation widget (and can otherwise serve as an old-API bridge)

            :param list of dicts data: must contains the keys 'counterpart_aml_dicts', 'payment_aml_ids' and 'new_aml_dicts',
                whose value is the same as described in process_reconciliation except that ids are used instead of recordsets.
        """
        data_bkp = data
        try:
            product_obj = self.env['product.product']
            if len(data) and 'new_aml_dicts' in data[0].keys() and len(data[0]['new_aml_dicts']):
                for line in data[0]['new_aml_dicts']:
                    if 'product_id' in  line.keys():
                        line['name'] = product_obj.browse(line['product_id']).name
        except:
            data = data_bkp
        AccountMoveLine = self.env['account.move.line']
        for st_line, datum in zip(self, data):
            payment_aml_rec = AccountMoveLine.browse(datum.get('payment_aml_ids', []))
            for aml_dict in datum.get('counterpart_aml_dicts', []):
                aml_dict['move_line'] = AccountMoveLine.browse(aml_dict['counterpart_aml_id'])
                del aml_dict['counterpart_aml_id']
            st_line.process_reconciliation(datum.get('counterpart_aml_dicts', []), payment_aml_rec,
                                           datum.get('new_aml_dicts', []))
