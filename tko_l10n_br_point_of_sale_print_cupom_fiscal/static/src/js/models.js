function tko_pos_store_cnpj_cpf(instance, module){ //module is instance.point_of_sale
        var QWeb = instance.web.qweb;
	    var _t = instance.web._t;
	    var round_di = instance.web.round_decimals;
	    var round_pr = instance.web.round_precision
	    
	    
	    module.PosModel.prototype.models.filter(function (m)
	    		 { return m.model === 'pos.session'; }).map(function (m) {
	    		  return m.fields.push('confirm_payment'), 
	    		  m;
	    		   });
	    // load model pos.config.journal.tko.rel
	    module.PosModel.prototype.models.push({
            model:  'pos.config.journal.tko.rel',
            fields: ['id','journal_id','config_id','fiscal_code'],
            loaded: function(self,fiscal_codes){ self.fiscal_codes = fiscal_codes; },
        });
	    	     
	    	      
	    
	    
	
	//FIX ME : extend to update cnpj_cpf in method only
	var OrderSuper = module.Order;
	

	module.Order = module.Order.extend({
		export_as_JSON: function() {
			var res = OrderSuper.prototype.export_as_JSON.call(this);
			var cnpj_cpf = this.attributes.cnpj_cpf || "";
			res.uid = String(res.uid).replace(/\D/g,'');
			res.name = res.uid;
		    res.cnpj_cpf = cnpj_cpf;
		    return res;
		},
		
		 get_client_address: function(){
	            var client = this.get('client');
	            return client ? client.address : "";
	     },
	     
	     get_client_cnpj_cpf: function(){
	            var client = this.get('client');
	            return client ? client.cnpj_cpf : "";
	     },
	
	});
	
	//FIX ME : extend to update cnpj_cpf in method only
	var OrderlineSuper = module.Orderline;
	module.Orderline = module.Orderline.extend({
		
		compute_all: function(taxes, price_unit) {
	        var self = this;
	        var res = [];
	        var currency_rounding = this.pos.currency.rounding;
	        if (this.pos.company.tax_calculation_rounding_method == "round_globally"){
	           currency_rounding = currency_rounding * 0.00001;
	        }
	        var base = price_unit;
	        _(taxes).each(function(tax) {
	            if (tax.tax_code_id_tax_discount) {
	                if (tax.type === "percent") {
	                    tmp =  round_pr(base - round_pr(base / (1 + tax.amount),currency_rounding),currency_rounding);
	                    data = {amount:tmp, price_include:true, id: tax.id, tax_code_id_tax_discount : tax.tax_code_id_tax_discount};
	                    res.push(data);
	                } else if (tax.type === "fixed") {
	                    tmp = tax.amount * self.get_quantity();
	                    data = {amount:tmp, price_include:true, id: tax.id, tax_code_id_tax_discount : tax.tax_code_id_tax_discount};
	                    res.push(data);
	                } else {
	                    throw "This type of tax is not supported by the point of sale: " + tax.type;
	                }
	            } else {
	                if (tax.type === "percent") {
	                    tmp = round_pr(tax.amount * base, currency_rounding);
	                    data = {amount:tmp, price_include:false, id: tax.id, tax_code_id_tax_discount : tax.tax_code_id_tax_discount};
	                    res.push(data);
	                } else if (tax.type === "fixed") {
	                    tmp = tax.amount * self.get_quantity();
	                    data = {amount:tmp, price_include:false, id: tax.id, tax_code_id_tax_discount : tax.tax_code_id_tax_discount};
	                    res.push(data);
	                } else {
	                    throw "This type of tax is not supported by the point of sale: " + tax.type;
	                }

	                var base_amount = data.amount;
	                var child_amount = 0.0;
	                if (tax.child_depend) {
	                    res.pop(); // do not use parent tax
	                    child_tax = self.compute_all(tax.child_taxes, base_amount);
	                    res.push(child_tax);
	                    _(child_tax).each(function(child) {
	                        child_amount += child.amount;
	                    });
	                }
	                if (tax.include_base_amount) {
	                    base += base_amount + child_amount;
	                }
	            }
	        });
	        return res;
	    },
		
		get_all_prices: function(){
            var base = round_pr(this.get_quantity() * this.get_unit_price() * (1.0 - (this.get_discount() / 100.0)), this.pos.currency.rounding);
            var totalTax = base;
            var totalNoTax = base;
            var taxtotal = 0;

            var product =  this.get_product();
            var taxes_ids = product.taxes_id;
            var taxes =  this.pos.taxes;
            var taxdetail = {};
            var product_taxes = [];

            _(taxes_ids).each(function(el){
                product_taxes.push(_.detect(taxes, function(t){
                    return t.id === el;
                }));
            });

            var all_taxes = _(this.compute_all(product_taxes, base)).flatten();

            _(all_taxes).each(function(tax) {
                if (tax.price_include) {
                    totalNoTax -= tax.amount;
                } else {
                    totalTax += tax.amount;
                }
                if (! tax.tax_code_id_tax_discount){
                	taxtotal += tax.amount;
                	taxdetail[tax.id] = tax.amount;
                }
                
                
            });
            totalNoTax = round_pr(totalNoTax, this.pos.currency.rounding);

            return {
                "priceWithTax": totalTax,
                "priceWithoutTax": totalNoTax,
                "tax": 0 , //taxtotal, we do not want to add taxes in pos UI
                "taxDetails": taxdetail,
            };
        },
	});
	
	
	
	
	module.OnscreenKeyboardWidget = module.OnscreenKeyboardWidget.extend({
		init: function(parent, options){
			this._super(parent,options);
			this.state = 'alphanumeric';
			
		},
		
		//What happens when numlock is pressed : toggle symbols and numlock label 
        toggleNumLock: function(){
            $('.symbol span').toggle();
            $('.numlock span').toggle();
            self.numlock = (self.numlock === true ) ? false : true;
            if (this.state === 'alphanumeric'){
            	this.state = 'numeric';
            }
            else{
            	this.state = 'alphanumeric';
            }
        },
        
        
        
        start: function(){
        	this._super();
        	var self = this;
        	
        	$('.clear_input').click(function(){ 
        		self.deleteAllCharacters();
            });
        	
        }
		
	
	});
	
}
