function tko_pos_fiscal_printer_control(instance, module){ //module is instance.point_of_sale
        var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	
	
	// create print button widget
	module.PrintButtonOptions = module.PosBaseWidget.extend({
		template: 'PrinterControlOptions',
		init: function(parent, options){
		    options = options || {};
		    this._super(parent, options);
		    this.action = options.action;
		    this.label   = options.label;
		},
		renderElement: function(){
		    var self = this;
		    this._super();
		    if(this.action){
		        this.$el.click(function(){
		            self.action();
		        });
		    }
		},
		show: function(){ this.$el.removeClass('oe_hidden'); },
		hide: function(){ this.$el.addClass('oe_hidden'); },
	    });
	
	module.PrintButtonWidget = module.PosBaseWidget.extend({
		template: 'PrinterControlWidget',
		init: function(parent, options){
		    options = options || {};
		    this._super(parent, options);
		    this.action = options.action;
		    this.label   = options.label;
		},
		renderElement: function(){
		    var self = this;
		    this._super();
		    if(this.action){
		        this.$el.click(function(){
		            self.action();
		        });
		    }
		},
		show: function(){ this.$el.removeClass('oe_hidden'); },
		hide: function(){ this.$el.addClass('oe_hidden'); },
	    });
	    
	
	// inherit PosWidget to add printer control widget in top right header
	module.PosWidget = module.PosWidget.extend({
		build_widgets: function() 
		{
			this._super();
			this.fiscal_print_button = new module.PrintButtonWidget(this,{
			label: _t('Print'),
			icon: '/tko_l10n_br_point_of_sale_print_cupom_fiscal/static/src/img/icons/png48/printer.png',
			action: function(){ 
				    var command = $('#printer-control-options').val();
				    smoke.confirm("Do you confirm action?", function(confirmed){
				    	if(confirmed){
				    		try{
				            	if (command === 'r_z'){
					            	console.log('print button pressed r_z ....',command);
					            	appECF.executaReducaoZ();
					            }else if (command === 'l_x'){
					            	console.log('print button pressed l_x ....',command);
					            	appECF.executaLeituraX();
					            }else if (command === 'c_c'){
					            	console.log('print button pressed c_c ....',command);
					            	appECF.executaCancelarUltimoCupom();
					            }else if (command === 'a_g'){
					            	console.log('print button pressed a_g....',command);
					            	appECF.abrirGaveta();
					            }else{
					            	console.log('print button pressed - - ....',command);
					            }
				            }catch (e) {
				            	
				                smoke.alert ("Please check if java applet is correctly loaded");
				                return false;
				            }
				    	}
				    	
				    });
				    
             },

			});
			// add print button in right header 
			this.fiscal_print_button.appendTo(this.$('.pos-rightheader'));
			
			this.fiscal_print_button_options = new module.PrintButtonOptions(this,{
				label: _t('Print'),
				action: function(){ 
			            console.log('print button options  pressed....');
			           
	               		 },

				});
				// add print button in right header 
			this.fiscal_print_button_options.appendTo(this.$('.pos-rightheader'));
			
		}
	});
	
	
	// Load Fiscal Printer Applet 
};
