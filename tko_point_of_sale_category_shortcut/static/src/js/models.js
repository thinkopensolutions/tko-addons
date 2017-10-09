function pos_category_shortcut(instance, module){ //module is instance.point_of_sale
	var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	module.PosModel.prototype.models.filter(function (m)
	 { return m.model === 'pos.category'; }).map(function (m) {
	  return m.fields.push('pos_shortcut'), 
	  m;
	   });
	   
	
	
};


		   
		  
       	   

       	      
     
