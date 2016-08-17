function tko_pos_print_receipt(instance, module){ //module is instance.point_of_sale
        var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	
	
	// create print button widget
	module.PrintButtonWidget = module.PosBaseWidget.extend({
		template: 'PrinterButtonWidget',
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
	    
	// create applet
	module.FiscalPrintWidget = module.PosBaseWidget.extend({
		template: 'FiscalAppletWidget',
		init: function(parent, options){
		    this._super();
		    this._super(parent, options);
		    //this.pos = new module.PosModel(this.session,{pos_widget:this});
		    this.action = options.action;
		    this.label   = 'Fiscal';
		    this.port = this.pos_widget.pos.config.com_port;
		    this.model = this.pos_widget.pos.config.printer_model;
		    this.baudrate = this.pos_widget.pos.config.baudrate;
		    this.federal_tax = this.pos.company.average_federal_tax;
		    this.state_tax = this.pos.company.average_state_tax;
 		},
		renderElement: function(){
		    var self = this;
		    this._super();
		    this.port = 999;
		    if(this.action){
		        this.$el.click(function(){
		            self.action();
		        });
		    }
		},
		show: function(){ this.$el.removeClass('oe_hidden'); },
		hide: function(){ this.$el.addClass('oe_hidden'); },
	    });
	
	// inherit PosWidget to add print button in top right header
	module.PosWidget = module.PosWidget.extend({
		build_widgets: function() 
		{
			this._super();
			this.print_button = new module.PrintButtonWidget(this,{
			label: _t('Print'),
			icon: '/tko_l10n_br_point_of_sale_print_cupom_fiscal/static/src/img/icons/png48/printer.png',
			action: function(){ 
		            console.log('print button pressed....');
		           
               		 },

			});
			// add print button in right header 
			//this.print_button.appendTo(this.$('.pos-rightheader'));
			
		}
	});
	
	
	// Load Fiscal Printer Applet 
	module.PosWidget = module.PosWidget.extend({
		build_widgets: function() 
		{
			this._super();
			this.fiscal_print_applet = new module.FiscalPrintWidget(this,{
			label: _t('Applet'),
			icon: '/tko_l10n_br_point_of_sale_print_cupom_fiscal/static/src/img/icons/png48/printer.png',
			action: function(){ 
		            console.log("FiscalPrintWidget button pressed....." );
               		 },

			});
			// load applet  button in right header 
			
			this.fiscal_print_applet.appendTo(this.$('.pos-rightheader'));
		}
	});
};
