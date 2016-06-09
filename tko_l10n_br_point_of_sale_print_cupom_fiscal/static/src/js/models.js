function tko_pos_store_cnpj_cpf(instance, module){ //module is instance.point_of_sale
        var QWeb = instance.web.qweb;
	    var _t = instance.web._t;
	    
	    
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
