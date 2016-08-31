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

import logging
import re
import time

from openerp import _
from openerp.osv import osv
from openerp.report import report_sxw

_logger = logging.getLogger(__name__)


class tko_contract_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(
            tko_contract_report,
            self).__init__(
            cr,
            uid,
            name,
            context=context)
        active_ids = context['active_ids']

        self.pool.get('account.analytic.account').check_fields(
            cr, uid, active_ids, context=context)
        self.localcontext.update({
            'time': time,
            'compute_template_variables': self.compute_template_variables,
        })

    def compute_template_variables(self, object, text):
        pattern = re.compile('\$\((.*?)\)s')
        matches = pattern.findall(str(text.encode('utf-8')))
        while len(matches):
            value = ''
            type = ''
            if len(matches):
                for match in matches:
                    value = object
                    block = match.split(',')
                    for field in block[0].split('.'):
                        try:
                            type = value._fields[field].type
                            if type != 'selection':
                                value = value[field]
                            else:
                                # get label for selection field
                                value = str(
                                    dict(
                                        value._model.fields_get(
                                            self.cr,
                                            self.uid,
                                            allfields=[field])[field]['selection'])[
                                        unicode(
                                            value[field]).encode('utf-8')])
                        except Exception as err:
                            value = (
                                        '<font color="red"><strong>[ERROR: Field %s doesn\'t exist  in %s]<strong></font>') % (
                                    err, value)
                            _logger.error(
                                ("Field %s doesn't exist  in %s") %
                                (err, value))
                    if value:
                        if type != 'binary':
                            text = text.replace(
                                '$(' + match + ')s', str(unicode(value).encode('utf-8')).decode('utf-8'))

                        else:
                            width, height = '', ''
                            try:
                                if block[1]:
                                    width = ' width="%spx"' % block[1]
                                if block[2]:
                                    height = ' height="%spx"' % block[2]
                                text = text.replace(
                                    '$(' + match + ')s', '<img src="data:image/jpeg;base64,' + str(value) + '"%s%s/>' %
                                    (width, height))
                            except Exception as err:
                                value = _(
                                    u'<font color="red"><strong>[ERROR: Wrong image size indication in "%s". Examples: "(partner_id.image,160,160)" or "(partner_id.image,,160)" or "(partner_id.image,160,)" or "(partner_id.image,,)"]<strong></font>' %
                                    match)
                                _logger.error(
                                    _(
                                        u'Wrong image size indication in "$(%s)s". Examples: $(partner_id.image,160,160)s or $(partner_id.image,,160)s or $(partner_id.image,160,)s or $(partner_id.image,,)s' % match))
                                text = text.replace(
                                    '$(' + match + ')s', str(value))

                    if not value:
                        text = text.replace('$(' + match + ')s', '')
            matches = pattern.findall(str(text.encode('utf-8')))
        return text


class report_tko_contract_report(osv.AbstractModel):
    _name = 'report.tko_account_contract_report_template.tko_contract_report'
    _inherit = 'report.abstract_report'
    _template = 'tko_account_contract_report_template.tko_contract_report'
    _wrapped_report_class = tko_contract_report
