
function pos_discount_cards_widgets(instance, module){ //module is instance.point_of_sale
        var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	
    //Create widget for PaymentScreen Discounts 
    module.PaymentScreenDiscountWidget = module.PosBaseWidget.extend({
        template: 'PaymentScreenDiscountWidget',
        init: function(parent, options){
            var self = this;
            this._super(parent,options);
            this.hidden = false;
        },
        
        
 
        
        start: function(options){
            var self = this;
            this._super();

            this.renderElement();
            
           
        },
        
        //actions to be taken on change of discount card
        discount_card_change: function(name){
            self = this;      
            //update total on product and payment screen 
            this.pos_widget.order_widget.update_summary();
            this.pos_widget.payment_screen.update_payment_summary();

            
        },
        
        get_cur_pos_config_id: function(){
		    var self = this;
		    var config = this.pos.config;
		    var config_id = null;
		             
		    if(config){
		        config_id = config.id;
		        
		        return config_id;
		    }        
		    return '';    
		},
        
        get_discount_cards: function(config_id){
            var self = this;
            var discount_card_list = [];
            
           
		    var cards = this.pos.cards;
            var discount_cards = []

            _.each(cards, function(card){
                discount_card_list.push([card.id, card.value, card.type, card.name,  ])
            });

            
            if(discount_card_list.length){
                self.$('#discount-card-select').html('<option value=""></option>')
                for(var i = 0, len = discount_card_list.length; i < len; i++){
                    if ($('#discount-card-select').length){


                    var content = self.$('#discount-card-select').html();
                    var new_option = '<option value="' + discount_card_list[i][0] + ':'+ discount_card_list[i][1] +':' + discount_card_list[i][2] +'">' + discount_card_list[i][3] + '</option>\n';
                    $('#discount-card-select').html('<option value=""></option><option value="1:20:fi">Fixed 20 %</option>');
                    console.log("final content............",content + new_option)
                    console.log($('[id="discount-card-select"]').length);
                    console.log($('#discount-card-select').length);
                    }
                    }                
            } 

            //FIX ME : apply domain in next line
            //var loaded = self.fetch('pos.discount.cards',['id', 'name','value' , 'type'],[['pos_config_id','=', config_id], ['active', '=','true']])
            /*var loaded = self.fetch('pos.discount.cards',['id', 'name','value' , 'type'],[['active', '=','true']])
            .then(function(discounts_cards){
                     for(var i = 0, len = discounts_cards.length; i < len; i++){
                        discount_card_list.push(discounts_cards[i].name);
                     }
		      
                    if(discount_card_list.length > 0){
                        self.$('#discount-card-select').html('<option value=""></option>')
                        for(var i = 0, len = discount_card_list.length; i < len; i++){
                            
                            var content = self.$('#discount-card-select').html();
                            var new_option = '<option value="' + discounts_cards[i].id + ':'+ discounts_cards[i].value +':' + discounts_cards[i].type +'">' + discount_card_list[i] + '</option>\n';
                            self.$('#discount-card-select').html(content + new_option);
                            }

                       

                    } 
                });*/
        }, 
        
        


	fetch: function(model, fields, domain, ctx){
            return new instance.web.Model(model).query(fields).filter(domain).context(ctx).all();
        },
        
        
    renderElement: function() {
        var self = this;
        this._super();
	
    self.$('#discount-card-select').change(function(){
            var name = this.value;
            self.discount_card_change(name);
        });
        
    },
        
        
        

       
       
        
    });
    
    
    module.PosWidget = module.PosWidget.extend({
    	build_widgets: function() {
            var self = this;
            this._super();
            this.discount_card_widget = new module.PaymentScreenDiscountWidget(this, {});
            this.discount_card_widget.replace($('.placeholder-PaymentScreenDiscountWidget'));
            
            },
    
    });
    
    
    // compute discount of 
    
   
var OrderSuper = module.Order;
module.Order = module.Order.extend({
	
	
	//send discount_card_id to write in database
	export_as_JSON: function() {
		var res = OrderSuper.prototype.export_as_JSON.call(this);
		var discount_card = self.$('#discount-card-select').val();
		if (discount_card){
			res.discount_card_id = discount_card.split(':')[0];
		}
	    
	    return res;
	},
	
	
	//this method returns discount given by discount card
	getDiscountCard : function(){
		var discount_val = self.$('#discount-card-select').val();
        var subtotal = (this.get('orderLines')).reduce((function(sum, orderLine) {
            return sum + orderLine.get_price_with_tax();
        }), 0);
        var discount = 0.0;
        var total = 0.0
        if (discount_val)
            {
                discount_data = discount_val.split(':')
                discount_value = discount_data[1]
                discount_type = discount_data[2]
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
          
            var discount_val = self.$('#discount-card-select').val();
            var subtotal = (this.get('orderLines')).reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_with_tax();
            }), 0);
            var discount = 0.0;
            var total = 0.0
            if (discount_val)
                {
                    discount_data = discount_val.split(':')
                    discount_value = discount_data[1]
                    discount_type = discount_data[2]
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
		
	    this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(final_tax );
	    this.el.querySelector('.summary .total .discount .value').textContent = this.format_currency(-discount);
	    
	    
    },
	});










} //end of code
