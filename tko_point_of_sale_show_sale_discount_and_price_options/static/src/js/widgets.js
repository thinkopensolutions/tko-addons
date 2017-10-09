function tko_pos_price_discount(instance, module){ //module is instance.point_of_sale
        var QWeb = instance.web.qweb;
	    var _t = instance.web._t;
	    
	    
	    module.PosModel.prototype.models.filter(function (m)
	    		 { return m.model === 'pos.session'; }).map(function (m) {
	    		  return m.fields.push('allow_disc', 'allow_price'), 
	    		  m;
	    		   });
	    
	    
	    
	    
	    // inherit to disable discount and price button on numpad
	    module.OrderWidget = module.OrderWidget.extend({
	    	set_value: function(val) {
	        	var order = this.pos.get('selectedOrder');
	        	if (this.editable && order.getSelectedLine()) {
	                var mode = this.numpad_state.get('mode');
	                if( mode === 'quantity'){
	                    order.getSelectedLine().set_quantity(val);
	                }else if( mode === 'discount' && this.pos.config.allow_disc === true){
	                    order.getSelectedLine().set_discount(val);
	                }else if( mode === 'price' && this.pos.config.allow_price === true){
	                    order.getSelectedLine().set_unit_price(val);
	                }
	        	}
	        },

	     
	      
	       
	    });

}
