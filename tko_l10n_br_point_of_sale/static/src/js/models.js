
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


		   
		  
       	   

       	      
     
