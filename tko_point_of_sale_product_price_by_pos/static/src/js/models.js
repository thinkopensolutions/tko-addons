function pos_price_exception_model(instance, module){ //module is instance.point_of_sale
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    module.PosModel.prototype.models.filter(function (m)
     { return m.model === 'pos.session'; }).map(function (m) {
      return m.fields.push('price_exception_ids'), 
      m;
       });

    module.PosModel.prototype.models.filter(function (m)
    	     { return m.model === 'product.product'; }).map(function (m) {
    	      return m.fields.push('price_exception'), 
    	      m;
    	       });
    
    
    module.PosModel.prototype.models.push(
            {
                model:  'pos.price.exception',
                fields: ['list_price', 'config_id', 'template_id' ],
                loaded: function(self,exceptions){ 
                	//filter price exceptions of current POS
                    self.price_exceptions = exceptions;//exceptions.filter(function(e){return e.config_id[0] === self.config.session_ids[1]});
                    
                }
            }
    )
    
	var OrderlineSuper = module.Orderline;
	module.Orderline = module.Orderline.extend({
		initialize: function(attr,options){
			OrderlineSuper.prototype.initialize.apply(this, arguments);
            this.price   = this.get_price_exception(options.product);//options.product.price;
        },
        
        
        get_price_exception: function(product){
        	price = 0.0
        	for (var i = 0; i < this.pos.price_exceptions.length; i++) {
        		if (this.pos.price_exceptions[i].template_id[0]=== product.product_tmpl_id && this.pos.price_exceptions[i].config_id[0] === this.pos.pos_session.config_id[0])
        			{
        			price = this.pos.price_exceptions[i].list_price
        			break;
        			}
        	}
        	if (price != 0.0){
        		return price
        	}
        	else{
        		return product.price
        	}
        },
	});	    
};
