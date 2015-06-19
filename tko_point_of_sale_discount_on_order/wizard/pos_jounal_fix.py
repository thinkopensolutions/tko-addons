from openerp.osv import osv, fields

class pos_journal_fix(osv.osv):
    _name = 'pos.journal.fix'
    
    _columns ={
               'corrected_ordes' :  fields.text('Corrected Orders'),
               }
    
    def pos_journal_fix(self, cr, uid, ids, context = None):
        order_obj = self.pool.get('pos.order')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        statement_obj = self.pool.get('account.bank.statement.line')
        pos_orders = order_obj.search(cr, uid, [])
        for order in order_obj.browse(cr, uid, pos_orders, context = context):
            for line in order.statement_ids:
                if line.amount > 1000:
                    print "amount seems not  okay %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%.........",order.name,line.amount
                    if line.amount > 1000:
                        statement_obj.write(cr, uid, [line.id], {'amount' : order.amount_total})
                        for move_line in line.journal_entry_id.line_id:
                            if move_line.credit > 0:
                                cr.execute("update account_move_line set credit=%s where id=%s"%(order.amount_total, move_line.id) )
                                #move_line_obj.write(cr, uid, [move_line.id], {'credit' : order.amount_total} )
                            if move_line.debit > 0:
                                cr.execute("update account_move_line set debit=%s where id=%s"%(order.amount_total, move_line.id) )
                                #move_line_obj.write(cr, uid, [move_line.id], {'debit' : order.amount_total} )
                        udpate_statement_ids = statement_obj.search(cr, uid, [('pos_statement_id','=',order.id),('id','!=',line.id)])
                        statement_obj.write(cr, uid, udpate_statement_ids, {'amount' : 0})
                        for statement in statement_obj.browse(cr, uid, udpate_statement_ids):
                            if statement.journal_entry_id:
                                for move_line in statement.journal_entry_id.line_id:
                                    #print "move id......................",move_line.move_id.id, move_line.move_id.name
                                    move_obj.button_cancel(cr, uid, [move_line.move_id.id])
                                move_obj.unlink(cr, uid, [statement.journal_entry_id.id])
                #statement_obj.unlink(cr, uid, [line.id])
                                    #move_line_obj.write(cr, uid, [move_line.id], {'debit' : 0, 'credit' :0} )
                         
        return True       
                
    