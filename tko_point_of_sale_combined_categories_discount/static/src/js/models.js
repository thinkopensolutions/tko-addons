function pos_category_combo_discount(instance, module){ //module is instance.point_of_sale
	var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	var round_pr = instance.web.round_precision;
	
	//to load for server disconnection
	module.PosModel.prototype.models.filter(function (m)
			 { return m.model === 'pos.session'; }).map(function (m) {
			  return m.fields.push('combo_ids'), 
			  m;
			   });
	
	//no need to load this model, we can't use without connection
	module.PosModel.prototype.models.push(
			{
	            model:  'pos.category.combo',
	            fields: ['main_category_id','disc_category_id', 'type', 'value' ],
	            loaded: function(self,combos){ 
	            	self.combos = combos;
	            	console.log("combos loaded.............................",combos)
	            }
	        }
	)
	
//	exetnd to add discounted field in orderline it helps to apply combo discount 
	
	
	
	//Extend orderline to add discounted flag
	var orderline_id = 1;
	var OrderlineSuper = module.Orderline;
	module.Orderline = module.Orderline.extend({
		initialize: function(attr,options){
			module.Orderline.__super__.initialize.call(this, attr, options);
            this.pos = options.pos;
            this.order = options.order;
            this.product = options.product;
            this.price   = options.product.price;
            this.quantity = 1;
            this.quantityStr = '1';
            this.discount = 0;
            this.discountStr = '0';
            this.type = 'unit';
            this.selected = false;
            this.id       = orderline_id++; 
            //add variable with lines to set discount
            this.discounted = false;
            this.categ_id = options.product.pos_categ_id[0]
            this.default_code = options.product.default_code;
            this.discount_type = 'p'
        },
        
        get_discount_type: function(){
            return this.discount_type;
        },
        
        get_base_price:    function(){
            var rounding = this.pos.currency.rounding;
            discount_type = this.get_discount_type();
            if (discount_type === 'fi'){
        		return round_pr(this.get_unit_price() * this.get_quantity() - (this.get_discount()), rounding);
        	}
            else
            	{
            	return round_pr(this.get_unit_price() * this.get_quantity() * (1 - this.get_discount()/100), rounding);
            	}
            	
            },
            
    		//send discount card type to write in database
    	    export_as_JSON: function() {
    	        var res = OrderlineSuper.prototype.export_as_JSON.call(this);
    	        res.discount_type = this.discount_type || false;
    	        return res;
    	    },
            
	});
	
	//Extend order to apply combo disocount each time a product is added
	module.Order = module.Order.extend({
		

		
		
		fetch: function(model, fields, domain, ctx){
            return new instance.web.Model(model).query(fields).filter(domain).context(ctx).all();
        },
        
        
		addProduct: function(product, options){
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            
            var line = new module.Orderline({}, {pos: this.pos, order: this, product: product});
            if(options.quantity !== undefined){
                line.set_quantity(options.quantity);
            }
            if(options.price !== undefined){
                line.set_unit_price(options.price);
            }
            if(options.discount !== undefined){
                line.set_discount(options.discount);
            }

            var last_orderline = this.getLastOrderline();
            if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                last_orderline.merge(line);
            }else{
                this.get('orderLines').add(line);
            }
            this.selectLine(this.getLastOrderline());
            
            
            //TODO call and super do things here 
            var combo_ids = [];
            var filter_combo_ids = [];
            var categ_id = product.pos_categ_id[0];
            var order = this.pos.get('selectedOrder');
            var orderlines = order.get('orderLines').models;
            var pair_index = false;
            var line_to_discount = false;
            var flag = false;
            var currentline = line;
            if(categ_id) {
            	if(this.pos){
            		var combos = this.pos.combos;
            		//get all combo options 
                	_.each(combos,function(combos){
//                		create array having [main_categ, disc_categ, type, value]
                		combo_ids.push([combos.main_category_id[0], combos.disc_category_id[0], combos.type, combos.value ]);
                    });
            	}
            	//filter array based on current product category
            	filter_combo_ids = _.filter(combo_ids, function(combo){
            		
            		return combo.indexOf(categ_id) !== -1;
            	});
            	//make discount on applicable line set line to be discounted
            	_.each(filter_combo_ids,function(combos){
//            		get other pair of current product's category id and search for that in exisiting lines
            		var discount_type = combos[2];
                    var disc_value = combos[3];
                    if (combos.indexOf(categ_id) === 0){
            			pair_index = 1
            		}
            		else{
            			pair_index = 0
            		}
            		pair_categ_id = combos[pair_index];
                    //search for all lines which are not discounted and having categ_id as pair_categ_id 
                    _.each(orderlines, function(line){

                        //if undiscounted but deserving lines
                        if (line.categ_id === pair_categ_id && line.discounted === false && !flag)
                        {
                            //check if last created or search line to be discounted
                            if (pair_index === 1){ //give discount to searched line
                                line_to_discount = line;
                            }
                            else{
                                line_to_discount = currentline;
                            }

                            if (discount_type === 'fi'){
                                line_to_discount.discount_type = 'fi';
                                line_to_discount.discountStr = 'fixed discount';
                                //set discount type for line
                                line.discount_type = 'fi';
                            }
                            else{
                            	line.discount_type = 'p';
                            }

                            //set discount and mark this line to be true
                            line_to_discount.set_discount(disc_value);
                            line.discounted = true;
                            currentline.discounted = true;
                            flag = true;

                        }
                    });
            		
//            		check if there is any line in order with id other than current product categ_id belonging to this array
            	});
            	}
            	
            
        },
		
	});
	
	
	
};


		   
		  
       	   

       	      
     
