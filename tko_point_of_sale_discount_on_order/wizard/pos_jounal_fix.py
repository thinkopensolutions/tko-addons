from openerp.osv import osv, fields

class pos_journal_fix(osv.osv):
    _name = 'pos.journal.fix'
    
    _columns ={
               'corrected_ordes' :  fields.text('Corrected Orders'),
               }
    
    def pos_journal_fix(self, cr, uid, ids, context = None):
        order_obj = self.pool.get('pos.order')
        statement_obj = self.pool.get('account.bank.statement.line')
        pos_orders = order_obj.search(cr, uid, [])
        corrected_ordes = ''
        for order in order_obj.browse(cr, uid, pos_orders, context = context):
            for line in order.statement_ids:
                if line.amount > 1000:
                    print "amount seems not  okay %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%.........",order.name,line.amount
                    if line.amount > 1000:
                        statement_obj.write(cr, uid, [line.id], {'amount' : order.amount_total})
                        udpate_statement_ids = statement_obj.search(cr, uid, [('pos_statement_id','=',order.id),('id','!=',line.id)])
                        statement_obj.write(cr, uid, udpate_statement_ids, {'amount' : 0})
                        corrected_ordes = corrected_ordes + ',' + order.name
        self.write(cr, uid, ids, {'corrected_orders' : corrected_ordes})
        return True       
                
    