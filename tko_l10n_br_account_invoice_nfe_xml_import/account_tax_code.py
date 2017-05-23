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
from openerp import fields, models


class account_tax_code(models.Model):
    _inherit = 'account.tax.code'

    account_collected_id = fields.Many2one('account.account', string=u'Invoice Tax Account')
    account_paid_id = fields.Many2one('account.account', string=u'Refund Tax Account')
    account_deduced_id = fields.Many2one('account.account', string=u'Tax Account for Deduction')
    account_paid_deduced_id = fields.Many2one('account.account', string=u'Tax Refund Account for Deduction')

    def _update_tax_code_account_first_install(self, cr, SUPERUSER_ID, ids=None, context=None):
        # get tax templates
        account_obj = self.pool.get('account.account')
        template_ids = self.pool.get('account.tax.code.template').search(cr, SUPERUSER_ID, [])
        tax_code_obj = self.pool.get('account.tax.code')
        tax_obj = self.pool.get('account.tax')

        for template in self.pool.get('account.tax.code.template').browse(cr, SUPERUSER_ID, template_ids):
            # get all account templates for current tax code template
            template_account_collected_id = template.account_collected_id
            template_account_paid_id = template.account_paid_id
            template_account_deduced_id = template.account_deduced_id
            template_account_paid_deduced_id = template.account_paid_deduced_id
            # find tax codes created by current tax code template
            tax_code_ids = tax_code_obj.search(cr, SUPERUSER_ID,
                                               [('code', '=', template.code), ('domain', '=', template.domain)])
            # itrate over each tax code from current tax code template and get all 4 types of accounts created by account templates
            for tax_code_id in tax_code_obj.browse(cr, SUPERUSER_ID, tax_code_ids):
                account_collected_id = account_obj.search(cr, SUPERUSER_ID,
                                                          [('company_id', '=', tax_code_id.company_id.id),
                                                           ('code', '=', template_account_collected_id.code)])
                account_paid_id = account_obj.search(cr, SUPERUSER_ID, [('company_id', '=', tax_code_id.company_id.id),
                                                                        ('code', '=', template_account_paid_id.code)])
                account_deduced_id = account_obj.search(cr, SUPERUSER_ID,
                                                        [('company_id', '=', tax_code_id.company_id.id),
                                                         ('code', '=', template_account_deduced_id.code)])
                account_paid_deduced_id = account_obj.search(cr, SUPERUSER_ID,
                                                             [('company_id', '=', tax_code_id.company_id.id),
                                                              ('code', '=', template_account_paid_deduced_id.code)])

                account_collected_id = len(account_collected_id) and account_collected_id[0] or False
                account_paid_id = len(account_paid_id) and account_paid_id[0] or False
                account_deduced_id = len(account_deduced_id) and account_deduced_id[0] or False
                account_paid_deduced_id = len(account_paid_deduced_id) and account_paid_deduced_id[0] or False
                # write all searched accounts on current tax code
                tax_code_obj.write(cr, SUPERUSER_ID, [tax_code_id.id], {'account_collected_id': account_collected_id,
                                                                        'account_paid_id': account_paid_id,
                                                                        'account_deduced_id': account_deduced_id,
                                                                        'account_paid_deduced_id': account_paid_deduced_id,
                                                                        })
                # search taxes for current tax code
                taxes_ids = tax_obj.search(cr, SUPERUSER_ID, [('base_code_id', '=', tax_code_id.id)])
                tax_obj.write(cr, SUPERUSER_ID, taxes_ids, {'account_collected_id': account_collected_id,
                                                            'account_paid_id': account_paid_id,
                                                            'account_deduced_id': account_deduced_id,
                                                            'account_paid_deduced_id': account_paid_deduced_id,
                                                            })
        return True


class account_tax_code_template(models.Model):
    _inherit = 'account.tax.code.template'

    account_collected_id = fields.Many2one('account.account.template', string=u'Invoice Tax Account')
    account_paid_id = fields.Many2one('account.account.template', string=u'Refund Tax Account')
    account_deduced_id = fields.Many2one('account.account.template', string=u'Tax Account for Deduction')
    account_paid_deduced_id = fields.Many2one('account.account.template', string=u'Tax Refund Account for Deduction')

    def generate_tax_code(self, cr, SUPERUSER_ID, tax_code_root_id, company_id,
                          context=None):
        """This function generates the tax codes from the templates of tax 
        code that are children of the given one passed in argument. Then it 
        returns a dictionary with the mappping between the templates and the 
        real objects.

        :param tax_code_root_id: id of the root of all the tax code templates 
                                 to process.
        :param company_id: id of the company the wizard is running for
        :returns: dictionary with the mappping between the templates and the 
                  real objects.
        :rtype: dict
        """
        tax_code_template_ref = super(account_tax_code_template, self).generate_tax_code(cr, SUPERUSER_ID,
                                                                                         tax_code_root_id, company_id,
                                                                                         context=context)
        return tax_code_template_ref
