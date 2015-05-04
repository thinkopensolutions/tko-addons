function pos_discount_cards_widgets(instance, module){ //module is instance.point_of_sale
        var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	
    //Create widget for PaymentScreen Discounts 
    module.PaymentScreenDiscountWidget = module.PosBaseWidget.extend({
        template: 'PaymentScreenDiscountWidget',
        init: function(parent, options){
            var self = this;
            this._super(parent,options);
            
           
           
        },

        
        start: function(options){
            var self = this;
            this._super();

            this.renderElement();
            
           
        },
        
        discount_card_change: function(name){
            self = this;
            globalDiscount = name;
            var order = this.pos.get('selectedOrder');
            var content = self.$('#discount-card-select').html();
            $('#discount-card-select').val(name);
            console.log("discount id...................",name);
            if (name)
            	{
		    var discont_line = self.fetch('pos.discount.cards',['type', 'value'],[['id','=', name]])
		    .then(function(discount)
		    {
		    	var type =  discount[0].type;
		    	var value = discount[0].value;
		    	$.each(order.get('orderLines').models, function (k, line){
			    line.set_discount(value)
			})
		    });
	    
		    
            }
            else{
	    	$.each(order.get('orderLines').models, function (k, line){
			    line.set_discount(0)
			})
	    
	    }
           
            
           
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
            
           
		
            //FIX ME : apply domain in next line
            var loaded = self.fetch('pos.discount.cards',['id', 'name'],[['pos_config_id','=', config_id], ['active', '=','true']])
            .then(function(discounts_cards){
                     for(var i = 0, len = discounts_cards.length; i < len; i++){
                        discount_card_list.push(discounts_cards[i].name);
                     }
		      
                    if(discount_card_list.length > 0){
                        self.$('#discount-card-select').html('<option value=""></option>')
                        for(var i = 0, len = discount_card_list.length; i < len; i++){
                            
                            var content = self.$('#discount-card-select').html();
                            var new_option = '<option value="' + discounts_cards[i].id + '">' + discount_card_list[i] + '</option>\n';
                            self.$('#discount-card-select').html(content + new_option);
                            }

                       

                    } 
                });
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
	  	      


} //end of code
