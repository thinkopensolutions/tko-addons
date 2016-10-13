
function l10n_br_fields(instance, module){ //module is instance.point_of_sale
	var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	module.PosModel.prototype.models.filter(function (m)
	 { return m.model === 'res.partner'; }).map(function (m) {
	  return m.fields.push('street2','cnpj_cpf'), 
	  m;
	   });
	   
	module.PosModel.prototype.models.filter(function (m)
	 { return m.model === 'res.company'; }).map(function (m) {
	  return m.fields.push('average_federal_tax','average_state_tax','order_reference'), 
	  m;
	   });
	
	// load domain in taxes
	module.PosModel.prototype.models.filter(function (m)
			 { return m.model === 'account.tax'; }).map(function (m) {
			  return m.fields.push('domain','tax_code_id_tax_discount'), 
			  m;
			   });
	// load NCM of product
	module.PosModel.prototype.models.filter(function (m)
			 { return m.model === 'product.product'; }).map(function (m) {
			  return m.fields.push('fiscal_classification_id'),
			  m;
			   });
	
	// tax definition with tax codes
	module.PosModel.prototype.models.push({
            model:  'l10n_br_tax.definition.sale',
            fields: ['tax_id','tax_code_id','tax_domain','fiscal_classification_id'],
           
            loaded: function(self, tax_definitions){
                self.tax_definitions = tax_definitions;
            },
        
	});

	// tax definition with tax codes
	module.PosModel.prototype.models.push({
            model:  'account.tax.code',
            fields: ['name','code','pos_fiscal_code'],
           
            loaded: function(self, tax_codes){
                self.tax_codes = tax_codes;
            },
        
	});

	// sort products loaded by display name
	module.PosModel.prototype.models.push({
            model:  'product.product',
            fields: ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'ean13', 'default_code',
                     'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description',
                     'product_tmpl_id'],
            domain: [['sale_ok','=',true],['available_in_pos','=',true]],
            context: function(self){ return { pricelist: self.pricelist.id, display_default_code: false }; },
            loaded: function(self, products){
                products = _.sortBy( products, 'display_name');
                self.db.add_products(products);
            },
	});
	
    // inherit Orderline to update product and taxes detail on line
	var OrderlineSuper = module.Orderline;
	module.Orderline = module.Orderline.extend({

		get_ncm: function(){
            return this.get_product().fiscal_classification_id[0];
        },

        get_tax_code: function(tax_code_id){
        	var tax_codes = this.pos.tax_codes;
        	for (i=0; i<tax_codes.length; i++)
        	{
        		if (tax_codes[i].id === tax_code_id)
        		{
        			return tax_codes[i].pos_fiscal_code;
        		}
        	}
        },

		get_tax_icms_tax_code: function (product) {
			// filter taxes with domain icms and ncm of current product
			var fiscal_classification_id = product.fiscal_classification_id[0];
			var icms_tax_line = _.filter(this.pos.tax_definitions, function (tax_line) {
				return tax_line.fiscal_classification_id[0] == fiscal_classification_id && tax_line.tax_domain === 'icms';
			})
			var taxes = this.pos.taxes
			var icms_tax_id = undefined; // set icms tax_id
			var tax_code_id = undefined; // set tax_code_id
			var tax_amount = 0.0;

			if (icms_tax_line.length > 0) {
				// id of icms tax associated in line
				icms_tax_id = icms_tax_line[0].tax_id[0];
				// id of tax code associated in line
				tax_code_id = icms_tax_line[0].tax_code_id[0];

			}
			for (i = 0; i < taxes.length; i++) {
				// filter icms tax_id from product taxes
				if (taxes[i].id === icms_tax_id) {
					// consider discount will always be percent type
					tax_amount = taxes[i].amount * 100
				}

			}
			return [tax_code_id, tax_amount]
		},

        // commented because we will get taxes from sever while saving order
        // pass taxes from pos
    	//export_as_JSON: function() {
    	//	var res = OrderlineSuper.prototype.export_as_JSON.call(this);
    	//	res.taxes = this.get_tax_details();
    	//	return res;
        //},


        export_for_printing: function(){
        	var res = OrderlineSuper.prototype.export_for_printing.call(this);
        	res.product = this.get_product();
        	res.taxes = this.get_tax_details();
        	var tax_detail = this.get_tax_icms_tax_code(res.product);
        	res.icms_tax_code = tax_detail[0]
        	res.icms_tax_value = Number(parseFloat(tax_detail[1]).toFixed(2))
        	res.ncm = this.get_ncm();
        	return res;
            },
            
        
        
	});	    
	//module.PosModel.prototype.models[5].fields.push('street2','cnpj_cpf');
	
	// serach partner with cnpj_cpf
	module.PosDB.include({
		_partner_search_string: function(partner){
            var str =  partner.name;
            if(partner.ean13){
                str += '|' + partner.ean13;
            }
            if(partner.address){
                str += '|' + partner.address;
            }
            if(partner.phone){
                str += '|' + partner.phone.split(' ').join('');
            }
            if(partner.mobile){
                str += '|' + partner.mobile.split(' ').join('');
            }
            if(partner.email){
                str += '|' + partner.email;
            }
            if(partner.cnpj_cpf){
                str += '|' + partner.cnpj_cpf;
            }
            str = '' + partner.id + ':' + str.replace(':','') + '\n';
            return str;
        },
        
        // serach products with category names also
        _product_search_string: function(product){
            var str = product.display_name;
            if (product.ean13) {
                str += '|' + product.ean13;
            }
            if (product.default_code) {
                str += '|' + product.default_code;
            }
            if (product.description) {
                str += '|' + product.description;
            }
            if (product.description_sale) {
                str += '|' + product.description_sale;
            }
            if (product.pos_categ_id){
            	str += '|' + this.get_category_by_id(product.pos_categ_id[0]).name
            }
            var packagings = this.packagings_by_product_tmpl_id[product.product_tmpl_id] || [];
            for (var i = 0; i < packagings.length; i++) {
                str += '|' + packagings[i].ean;
            }
            str  = product.id + ':' + str.replace(/:/g,'') + '\n';
            return str;
        },
    })
	
	
};


		   
		  
       	   

       	      
     
