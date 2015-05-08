function pos_discount_cards_model(instance, module){ //module is instance.point_of_sale
	var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	module.PosModel.prototype.models.filter(function (m)
	 { return m.model === 'pos.session'; }).map(function (m) {
	  return m.fields.push('discount_card_ids'), 
	  m;
	   });

	module.PosModel.prototype.models.push(
			{
	            model:  'pos.discount.cards',
	            fields: ['name', 'type', 'value' , 'active' ],
	            loaded: function(self,cards){ 
	            	self.cards = cards;
	            	console.log("cards loaded.............................",cards)
	            }
	        }
	)
	   
	
	
};


		   
		  
       	   

       	      
     
