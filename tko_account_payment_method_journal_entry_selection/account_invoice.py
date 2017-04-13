from openerp import models, fields, api


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends(
        'move_id.line_ids'
    )
    def _get_receivable_lines(self):
        if self.move_id:
            data_lines = [x for x in self.move_id.line_ids if (
                x.account_id.id == self.account_id.id
                and x.account_id.type in ('receivable', 'payable')
                and self.journal_id.revenue_expense)]
            New_ids = []
            for line in data_lines:
                New_ids.append(line.id)
                New_ids.sort()
            self.move_line_receivable_id = New_ids

    move_line_receivable_id = fields.Many2many('account.move.line', compute='_get_receivable_lines',
                                               inverse='set_receivable_lines', string='Entry Lines')

    @api.multi
    def set_receivable_lines(self):
        for record in self:
            return True


class account_voucher(models.Model):
    _inherit = 'account.voucher'

    # update due date of created move line on voucher payment
    def voucher_move_line_create(self, line_total, move_id, company_currency, current_currency):
        result = super(account_voucher, self).voucher_move_line_create(line_total, move_id,
                                                                       company_currency, current_currency)
        voucher = self.env['account.voucher'].browse(self._id)
        move_lines = result[1][0]
        if len(result[1][0]) == 2:
            move_line = self.env['account.move.line'].browse([move_lines[0]])
            move_line.write({'date_maturity': voucher.move_line_id.date_maturity})
        return result
