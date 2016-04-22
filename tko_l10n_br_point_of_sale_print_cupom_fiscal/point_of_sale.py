# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
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
import logging
from openerp.exceptions import Warning
_logger = logging.getLogger(__name__)

PRINTER_MODELS = [('1', 'Não Fiscal'),
                  ('2', 'Bematech'),
                  ('3', 'Sweda'),
                  ('4', 'Daruma'),
                  ('5', 'Schalter'),
                  ('6', 'Mecaf'),
                  ('7', 'Yanco'),
                  ('8', 'DataRegis'),
                  ('9', 'Urano'),
                  ('10', 'ICash'),
                  ('11', 'Quattro'),
                  ('12', 'FiscNET'),
                  ('13', 'Epson'),
                  ('14', 'NCR'),
                  ('15', 'SwedaSTX'), ]

SERIAL_PORTS = [('COM1', 'COM1'),
                ('COM2', 'COM2'),
                ('COM3', 'COM3'),
                ('COM4', 'COM4'),
                ('COM5', 'COM5'),
                ('COM6', 'COM6'),
                ('COM7', 'COM7'),
                ('COM8', 'COM8'),
                ('COM9', 'COM9'),
                ('COM10', 'COM10'),
                ('COM11', 'COM11'),
                ('COM12', 'COM12'),
                ('COM13', 'COM13'),
                ('COM14', 'COM14'),
                ('COM15', 'COM15'), ]


class pos_session(models.Model):
    _inherit = 'pos.session'

    confirm_payment = fields.Boolean(
        string='Confirm Payment',
        related="config_id.confirm_payment",
        default=True)
    default_fiscal_code = fields.Integer('Default Fiscal Code', related="config_id.default_fiscal_code", required=True, help="If no fiscal code is matched default one is passed to fiscal printer")

class pos_config_journal_tko_rel(models.Model):
    _name = 'pos.config.journal.tko.rel'
    
    journal_id = fields.Many2one('account.journal', string=u'Payment Method')
    config_id = fields.Many2one('pos.config', string=u'POS Config')
    fiscal_code = fields.Char(u'Fiscal Code')
    
    _sql_constraints = [
        ('journal_pos_uniq', 'unique (journal_id,config_id)',
         'Duplicate Payment method in POS')
    ]
    
class pos_config(models.Model):
    _inherit = 'pos.config'

    com_port = fields.Selection(SERIAL_PORTS, 'COM Port',
                                required=True, default='COM2')
    printer_model = fields.Selection(PRINTER_MODELS, 'Printer Model',
                                     required=True, default='13')
    baudrate = fields.Integer('Baudrate',
                              required=True, default=9600)
    confirm_payment = fields.Boolean(string='Confirm Payment', default=True)
    default_fiscal_code = fields.Char('Default Fiscal Code', default='0', required=True, help="If no fiscal code is matched default one is passed to fiscal printer")
    tko_journal_ids = fields.One2many('pos.config.journal.tko.rel', 'config_id', string = u'Journal', ondelete="cascade")
    
    
    @api.constrains('tko_journal_ids','journal_ids')
    def _check_fiscal_codes(self):
        """
        Validate fiscal codes in payment methods
        """
        if len(self.tko_journal_ids) != len(self.journal_ids):
            raise Warning(_("Please Define fiscal codes for each payment method"))
class pos_order(models.Model):
    _inherit = 'pos.order'

    cnpj_cpf = fields.Char('CNPJ/CPF', size=20)

    def create_from_ui(self, cr, uid, orders, context=None):
        # Keep only new orders

        pos_obj = self.pool.get('pos.order')
        pos_line_object = self.pool.get('pos.order.line')
        table_reserved_obj = self.pool.get("table.reserverd")
        session_obj = self.pool.get('pos.session')
        shop_obj = self.pool.get('sale.shop')
        partner_obj = self.pool.get('res.partner')
        order_ids = super(
            pos_order,
            self).create_from_ui(
            cr,
            uid,
            orders,
            context=context)
        # write cnpj_cpf to order
        if len(order_ids) == len(orders):
            i = 0
            for tmp_order in orders:

                if 'data' in tmp_order.keys():
                    cnpj_cpf = tmp_order['data'].get('cnpj_cpf')

                    if cnpj_cpf:
                        cnpj_cpf = cnpj_cpf.replace(
                            '-',
                            '').replace(
                            '.',
                            '').replace(
                            ',',
                            '').replace(
                            '/',
                            '')
                        if len(cnpj_cpf) == 11:
                            cnpj_cpf = cnpj_cpf[
                                0:3] + '.' + cnpj_cpf[3:6] + '.' + cnpj_cpf[6:9] + '-' + cnpj_cpf[9:11]
                        elif len(cnpj_cpf) == 14:
                            cnpj_cpf = cnpj_cpf[0:2] + '.' + cnpj_cpf[2:5] + '.' + cnpj_cpf[
                                5:8] + '/' + cnpj_cpf[8:12] + '-' + cnpj_cpf[12:14]
                        else:
                            # this case should never happen for a validated cpf
                            # / cnpj
                            _logger.error("Please check CPF/CNPJ validator")
                        partner = partner_obj.search(
                            cr, uid, [('cnpj_cpf', '=', cnpj_cpf)])
                        pos_obj.write(
                            cr, uid, [
                                order_ids[i]], {
                                'cnpj_cpf': cnpj_cpf, 'partner_id': partner and partner[0] or False})
                    i = i + 1
        return order_ids
