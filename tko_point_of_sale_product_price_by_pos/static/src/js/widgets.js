
function pos_product_price_exception_widgets(instance, module){ //module is instance.point_of_sale
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    

    module.ProductListWidget = module.ProductListWidget.extend({
    	
    	 get_price_exception: function(product){
         	price = 0.0
         	for (var i = 0; i < this.pos.price_exceptions.length; i++) {
         		if (this.pos.price_exceptions[i].template_id[0]=== product.product_tmpl_id && this.pos.price_exceptions[i].config_id[0] === this.pos.pos_session.config_id[0])
         			{
         			price = this.pos.price_exceptions[i].list_price
         			break;
         			}
         	}
         	if (price != 0.0){
         		return price
         	}
         	else{
         		return product.price
         	}
         },
        
        
    	render_product: function(product){
            var cached = this.product_cache.get_node(product.id);
            if(!cached){
                var image_url = this.get_product_image_url(product);
                var product_html = QWeb.render('Product',{ 
                        widget:  this, 
                        product: product, 
                        image_url: this.get_product_image_url(product),
                        exception : this.get_price_exception(product),
                    });
                var product_node = document.createElement('div');
                product_node.innerHTML = product_html;
                product_node = product_node.childNodes[1];
                this.product_cache.cache_node(product.id,product_node);
                return product_node;
            }
            return cached;
        },
    });

} //end of code
