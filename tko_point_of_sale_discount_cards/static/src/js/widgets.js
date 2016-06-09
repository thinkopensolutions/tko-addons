
function pos_discount_cards_widgets(instance, module){ //module is instance.point_of_sale
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    

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
        var discount_value = self.$('.discount-card-select option:selected').attr('disc_value');
        var subtotal = (this.get('orderLines')).reduce((function(sum, orderLine) {
            return sum + orderLine.get_display_price(); //display price is computed with considering both discount types fixed and precentage 
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
                         discount = ((subtotal + this.getTax()) * discount_value)/100;
                    }
            }
        return discount;
    },

    getTotalTaxIncluded: function() {
        var subtotal = (this.get('orderLines')).reduce((function(sum, orderLine) {
            return sum + orderLine.get_display_price(); //display price is computed with considering both discount types fixed and precentage 
        }), 0);
        
        var discount = 0.0;
        var total = 0.0
        total = subtotal + this.getTax() - this.getDiscountCard();
        //include tax in total
        return total;
        }
});


module.OrderWidget = module.OrderWidget.extend({
	 renderElement: function() {
		 var self = this;
         this._super();
         this.el.querySelector('.discount-card-select-order').addEventListener('change',this.selectCard);
	 },
	 
	 // This will sync discount cards on payment screen widget
	 selectCard: function(e){
		 // after update payment summy discount card in order widget is set to None
	     // set back value of selected discount card from payment screen widget to order widget
		 //self.posmodel.pos_widget.order_widget.update_summary
		 $(".discount-card-select").val($('.discount-card-select-order option:selected').attr('value'));
		 // vistaalegre sometimes raises error on production
		 // code in catch block is specific to vistaalegre
		 try{
			 self.posmodel.pos_widget.order_widget.update_summary();
			 self.posmodel.pos_widget.payment_screen.update_payment_summary();
		 }
		 catch (err){
			 self.pos_widget.order_widget.update_summary();
			 self.pos_widget.payment_screen.update_payment_summary();
		 }
		 
	     },
    update_summary: function(){
        this._super();
        
        var order = this.pos.get('selectedOrder');
        var total     = order ? order.getTotalTaxIncluded() : 0;
        var discount     = order ? order.getDiscountCard() : 0;
        var taxes     = order ? order.getTax(): 0;
        if (total < 0){
            total = 0;
        }
        this.el.querySelector('.summary .total > .value').textContent = this.format_currency(total);
        this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(taxes );
        this.el.querySelector('.summary .total .discount .value').textContent = this.format_currency(-discount);
        // after update payment summy discount card in order widget is set to None
        // set back value of selected discount card from payment screen widget to order widget
        $(".discount-card-select-order").val($('.discount-card-select option:selected').attr('value'));
    },
    });
} //end of code
