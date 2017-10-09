openerp.tko_point_of_sale_product_price_by_pos = function(instance){

    var module = instance.point_of_sale;
    
    pos_price_exception_model(instance,module);
    pos_product_price_exception_widgets(instance, module);

    

};

