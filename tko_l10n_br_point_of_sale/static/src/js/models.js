
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
	  return m.fields.push('average_federal_tax','average_state_tax'), 
	  m;
	   });
	
	// load domain in taxes
	module.PosModel.prototype.models.filter(function (m)
			 { return m.model === 'account.tax'; }).map(function (m) {
			  return m.fields.push('domain'), 
			  m;
			   });
	// load NCM of product
	module.PosModel.prototype.models.filter(function (m)
			 { return m.model === 'product.product'; }).map(function (m) {
			  return m.fields.push('property_fiscal_classification'), 
			  m;
			   });
	
	// tax definition with tax codes
	module.PosModel.prototype.models.push({
            model:  'l10n_br_tax.definition.sale',
            fields: ['tax_id','tax_code_id','fiscal_classification_id'],
           
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
	
    // inherit Orderline to update product and taxes detail on line
	var OrderlineSuper = module.Orderline;
	module.Orderline = module.Orderline.extend({
		
		get_ncm: function(){
            return this.get_product().property_fiscal_classification[0];
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
        
        get_tax_icms_tax_code: function(product){
        	var taxes_ids = this.get_product().taxes_id;
        	var taxes =  this.pos.taxes;
        	var taxes_definations  = this.pos.tax_definitions;
        	var fiscal_classification_id = product.property_fiscal_classification[0];
        	var icms_tax_id = undefined; // set icms tax_id
        	var tax_amount = 0.0
        	
        	for (i = 0; i < taxes.length; i++) 
        		{
                // filter icms tax_id from product taxes
                if (taxes_ids.indexOf(taxes[i].id) !== -1 && taxes[i].domain === 'icms') {
                	icms_tax_id = taxes[i].id;
                	// consider discount will always be percent type
                	tax_amount = taxes[i].amount * 100
                }

            }
        	
        	if (icms_tax_id)
        		{
					for (i = 0; i < taxes_definations.length; i++) 
						{
							if (taxes_definations[i].id == fiscal_classification_id && taxes_definations[i].tax_id[0] === icms_tax_id)
							{
								// tax_code_id
								var tax_code_id = this.get_tax_code(taxes_definations[i].tax_code_id[0]);
								//return taxes_definations[i].tax_code_id
								break;
							}
						}
        	}
        	
        	return [tax_code_id,tax_amount]
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
    })
	
	
};


		   
		  
       	   

       	      
     
