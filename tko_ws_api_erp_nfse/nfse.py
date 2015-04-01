# -*- encoding: utf-8 -*-
##############################################################################
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
#
#    This program is NOT free software.
#
##############################################################################

from openerp import models, api, fields, _
from openerp.osv import osv
from datetime import datetime
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import workflow

INVOICE_STATES = [
                  ('draft','Draft'),
                  ('proforma','Pro-forma'),
                  ('proforma2','Pro-forma'),
                  ('create_validation','Creating NFSe'),
                  ('create_error','Error Creating NFSe'),
                  ('proforma2','Pro-forma'),
                  ('open','Open'),
                  ('paid','Paid'),
                  ('cancel_validation','Canceling NFSe'),
                  ('cancel_error','Error Canceling NFSe'),
                  ('cancel','Cancelled'),
                  ]

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    
    state = fields.Selection(INVOICE_STATES, string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")
    date_create_validation = fields.Datetime(u'Pedido de criação')
    date_create = fields.Datetime(u'Data de criação')
    date_cancel_validation = fields.Datetime(u'Pedido de cancelamento')
    date_cancel = fields.Datetime(u'Data de cancelamento')
    nfse_number = fields.Char(u'NFSe Número')
    nfse_city = fields.Many2one('l10n_br_base.city', u'Prefeitura',
        readonly=True)
    nfse_log_ids = fields.One2many('nfse.log', 'invoice_id',
        string='Comunicação com Prefeitura',
        readonly=True)
    
    @api.one
    def _compute_reconciled(self):
        self.reconciled = self.test_paid()
    
    @api.multi
    def action_create_nfse(self):
        nfse_log = self.env['nfse.log']
        for inv in self:
            ######
            # BASICS DATA TESTS :: CHECK ALL NECESSARY FIELDS
            ######
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if not inv.date_invoice:
                raise except_orm(_('No Invoice Date!'), _('Please insert invoice date.'))
            if inv.move_id:
                continue
            
            ######
            # INSERT CREATION REQUEST TO API CODE HERE
            ######
            values = {
                      'state': 'create_validation',
                      'date_create_validation': datetime.now(),
                      }
            self.write(values)
            nfse_log.create({'name':'Pedido de criação enviado', 'date': datetime.now(), 'invoice_id': inv.id})
        return True
    
    @api.multi
    def action_check_create_nfse(self):
        result = False
        moves = self.env['account.move']
        nfse_log = self.env['nfse.log']
        for inv in self:
            ######
            # INSERT CREATION VALIDATION REQUEST TO API CODE HERE
            ######
            # TODO: SET THIS result WITH API VALIDATION RESULT
            result = True
            values = {
                      # TODO: CHANGE THIS WITH INFO FROM API
                      'nfse_number': 'NF0000000XX', 
                      # TODO: CHANGE THIS WITH INFO FROM API
                      'nfse_city': 3144,
                      'state': 'open',
                      'date_create': datetime.now(),
                      }
            self.write(values)
            nfse_log.create({'name':'Pedido de cancelamento confirmado', 'date': datetime.now(), 'invoice_id': inv.id})
        return result
    
    @api.multi
    def action_cancel_nfse(self):
        moves = self.env['account.move']
        nfse_log = self.env['nfse.log']
        for inv in self:
            ######
            # BASICS DATA TESTS :: CHECK ALL NECESSARY FIELDS
            ######
            if inv.move_id:
                moves += inv.move_id
            if inv.payment_ids:
                for move_line in inv.payment_ids:
                    if move_line.reconcile_partial_id.line_partial_ids:
                        raise except_orm(_('Error!'), _('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))
            if not inv.move_id.journal_id.update_posted:
                raise osv.except_osv(_('Error!'), _('You cannot modify a posted entry of this journal.\nFirst you should set the journal to allow cancelling entries.'))
            
            ######
            # INSERT CANCELATION REQUEST TO API CODE HERE
            ######
            values = {
                      'state': 'cancel_validation',
                      'date_cancel_validation': datetime.now(),
                      }
            self.write(values)
            nfse_log.create({'name':'Pedido de cancelamento enviado', 'date': datetime.now(), 'invoice_id': inv.id})
        return True
    
    @api.multi
    def action_check_cancel_nfse(self):
        moves = self.env['account.move']
        nfse_log = self.env['nfse.log']
        for inv in self:
            ######
            # INSERT CANCELATION VALIDATION REQUEST TO API CODE HERE
            ######
            values = {
                      'state': 'cancel',
                      'date_cancel': datetime.now(),
                      }
            self.write(values)
            nfse_log.create({'name':'Pedido de cancelamento confirmado', 'date': datetime.now(), 'invoice_id': inv.id})
        return True
        
        
class nfse_log(models.Model):
    _name = "nfse.log"
    _description = "NFSe Log"
    
    name = fields.Char(u'Descrição', readonly=True)
    date = fields.Datetime(u'Data da mensagem', readonly=True)
    invoice_id = fields.Many2one('account.invoice', string='Invoice Reference',
        ondelete='cascade')
    
