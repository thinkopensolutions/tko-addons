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
        
        discount_card_change: function(name){
            globalDiscount = name;

            $('#pay-screen-cashier-name').html(name);
            //console.log('discount_card_change : ' + name);
            
            if(name != ''){
                $('.gotopay-button').removeAttr('disabled');                 
            } else{
                $('.gotopay-button').attr('disabled', 'disabled');
            }
        },
        
        get_cur_pos_config_id: function(){
		    var self = this;
		    var config = self.pos.get('pos_config');
		    var config_id = null;
		             
		    if(config){
		        config_id = config.id;
		        
		        return config_id;
		    }        
		    return '';    
		},
        
        get_discount_card: function(config_id){
            var self = this;
            var discount_card_list = [];
            
           


            var loaded = self.fetch('pos.discount.cards',['name'],[['pos_config_id','=', config_id], ['active', '=','true']])
                .then(function(discounts_cards){
                     for(var i = 0, len = discounts_cards.length; i < len; i++){
                        discount_card_list.push(discounts_cards[i].name);
                     }

                    if(discount_card_list.length > 0){
                        
                        for(var i = 0, len = discount_card_list.length; i < len; i++){
                            var content = self.$('#discount-card-select').html();
                            var new_option = '<option value="' + discount_card_list[i] + '">' + discount_card_list[i] + '</option>\n';
                            self.$('#discount-card-select').html(content + new_option);
                            }

                        self.$('#AlertNoCashier').css('display', 'none');
                        self.$('#discount-card-select').selectedIndex = 0;
                        globalDiscount = discount_card_list[0];
                        self.discount_card_change(globalDiscount);

                    } else{

                        // if there are no cashier
                        self.$('#AlertNoCashier').css('display', 'block');
                        self.$('.gotopay-button').attr('disabled', 'disabled');
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
        
        
        build_widgets: function() {
            var self = this;
            this._super();
            this.discount_card_widget = new module.OrderWidget(this, {});
            this.discount_card_widget.replace($('#placeholder-PaymentScreenDiscountWidget'));
            
            },

       
       
        
    });
	  	      


} //end of code
