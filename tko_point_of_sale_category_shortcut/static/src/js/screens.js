function pos_category_shortcut_screen(instance, module){ //module is instance.point_of_sale
    var QWeb = instance.web.qweb,
    _t = instance.web._t;

    var round_pr = instance.web.round_precision
     var ProductScreenWidgetSuper = module.ProductScreenWidget
     module.ProductScreenWidget = module.ProductScreenWidget.extend({
        
        
       
       start: function(){ 
            this._super();
         
            this.product_categories_shortcut_widget = new module.ProductCategoriesShortCutWidget(this,{
                product_list_widget: this.product_list_widget,
            });
            this.product_categories_shortcut_widget.replace(this.$('.placeholder-ProductCategoriesShortCutWidget'));
            
        },
        
        
   
   
    });
    
    
}
