# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import time
from openerp.osv import osv, orm
from openerp.report import report_sxw
from openerp.exceptions import Warning
from openerp import _
import re
import logging
_logger = logging.getLogger(__name__)


class tko_contract_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(tko_contract_report, self).__init__(cr, uid, name, context=context)
        active_ids = context['active_ids']
        
        self.pool.get('account.analytic.account').check_fields(cr, uid, active_ids, context=context)
        self.localcontext.update({
            'time': time,
            'compute_template_variables':self.compute_template_variables,
          
        })
        
    def compute_template_variables(self, object, text):
        pattern = re.compile('\$\((.*?)\)s')
        matches = pattern.findall(str(text))
        value = ''
        if len(matches):
            for match in matches:
                value = object
                block = match.split(',')
                for field in block[0].split('.'):
                    try:
                        type = value._fields[field].type
                        value = value[field]
                    except Exception, err:
                        value = ("field %s doesn't exist  in %s") % (err, value)
                        _logger.error(("field %s doesn't exist  in %s") % (err, value))
                if value:
                    if type != 'binary':
                        text = text.replace('$(' + match + ')s' , str(value))
                    else:
                        width, height = '', ''
                        try:
                            if block[1]:
                                width = ' width="%spx"' % block[1]
                            if block[2]:
                                height = ' height="%spx"' % block[2]
                        except Exception, err:
                            raise Warning(_(u'Wrong image size indication.\nExamples:\n $(partner_id.image,160,160)s\n $(partner_id.image,,160)s\n $(partner_id.image,160,)s\n $(partner_id.image,,)s'))
                        text = text.replace('$(' + match + ')s' , '<img src="data:image/jpeg;base64,' + str(value) + '"%s%s/>' % (width, height))
                    
                if not value:
                    text = text.replace('$(' + match + ')s' , '')
        return text
    
    
class report_tko_contract_report(osv.AbstractModel):
    _name = 'report.tko_account_contract_report_template.tko_contract_report'
    _inherit = 'report.abstract_report'
    _template = 'tko_account_contract_report_template.tko_contract_report'
    _wrapped_report_class = tko_contract_report
