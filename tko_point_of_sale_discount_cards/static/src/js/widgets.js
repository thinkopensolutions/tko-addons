
function pos_discount_cards_widgets(instance, module){ //module is instance.point_of_sale
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    
    
    /*self.$('#discount-card-select').change(function(){
        var name = this.value;
        self.discount_card_change(name);
    })*/

    module.PaymentScreenWidget = module.PaymentScreenWidget.extend({
        
        events: {
            "change .discount-card-select": "selectCard" 
        },

        selectCard: function(e){
            this.pos_widget.order_widget.update_summary();
            this.pos_widget.payment_screen.update_payment_summary();
            },
            
            
        update_payment_summary: function() {
            this._super();
            var currentOrder = this.pos.get('selectedOrder');
            var selected = $('#discount-card-select option:selected').attr('value');
            var paidTotal = currentOrder.getPaidTotal();
            var dueTotal = currentOrder.getTotalTaxIncluded();
            var remaining = dueTotal > paidTotal ? dueTotal - paidTotal : 0;
            var change = paidTotal > dueTotal ? paidTotal - dueTotal : 0;
            if (dueTotal< 0){
                dueTotal = 0;
                remaining = 0;
                change = 0;
            }
            this.$('.payment-due-total').html(this.format_currency(dueTotal));
            this.$('.payment-remaining').html(this.format_currency(remaining));
            this.$('.payment-change').html(this.format_currency(change));
            if(currentOrder.selected_orderline === undefined){
                remaining = 1;  // What is this ? 
            }
                
            if(this.pos_widget.action_bar){
                this.pos_widget.action_bar.set_button_disabled('validation', !this.is_paid());
                this.pos_widget.action_bar.set_button_disabled('invoice', !this.is_paid());
            }
        },
    });


// compute discount of
var OrderSuper = module.Order;
module.Order = module.Order.extend({
    //send discount_card_id to write in database
    export_as_JSON: function() {
        var res = OrderSuper.prototype.export_as_JSON.call(this);
        var discount_card_id = self.$('.discount-card-select option:selected').attr('id');
        res.discount_card_id = discount_card_id || false;
        
        return res;
    },
    
    //this method returns discount given by discount card
    getDiscountCard : function(){
        var discount_id = self.$('.discount-card-select option:selected').attr('id');
        var discount_type = self.$('.discount-card-select option:selected').attr('type');
        var discount_value = self.$('.discount-card-select option:selected').attr('value');
        var subtotal = (this.get('orderLines')).reduce((function(sum, orderLine) {
            return sum + orderLine.get_price_with_tax();
        }), 0);
        var discount = 0.0;
        var total = 0.0
        if (discount_type && discount_value)
            {
                if (discount_type === 'fi')
                    {
                        discount = discount_value;
                    }
                else
                    {
                         discount = (subtotal * discount_value)/100;
                    }
            }
        return discount;
    },

    getTotalTaxIncluded: function() {
        var discount_id = self.$('.discount-card-select option:selected').attr('id');
        var discount_type = self.$('.discount-card-select option:selected').attr('type');
        var discount_value = self.$('.discount-card-select option:selected').attr('value');
        
        var subtotal = (this.get('orderLines')).reduce((function(sum, orderLine) {
            return sum + orderLine.get_price_with_tax();
        }), 0);
        
        var discount = 0.0;
        var total = 0.0
        if (discount_type && discount_value)
            {
                if (discount_type === 'fi')
                    {
                        discount = discount_value;
                    }
                else
                    {
                         discount = (subtotal * discount_value)/100;
                    }
            }
        total = subtotal - discount;
        return total;
        }
});


module.OrderWidget = module.OrderWidget.extend({
    update_summary: function(){
        this._super();
        
        var order = this.pos.get('selectedOrder');
        var total     = order ? order.getTotalTaxIncluded() : 0;
        var discount     = order ? order.getDiscountCard() : 0;
        var taxes     = order ? order.getTotalTaxExcluded(): 0;
        final_tax = Number(total) + Number(discount) - Number(taxes) 
        if (total < 0){
            total = 0;
        }
        this.el.querySelector('.summary .total > .value').textContent = this.format_currency(total);
        this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(final_tax );
        this.el.querySelector('.summary .total .discount .value').textContent = this.format_currency(-discount);
    },
    });
} //end of code
