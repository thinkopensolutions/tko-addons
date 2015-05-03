function tko_pos_widgets(instance, module){ //module is instance.point_of_sale
        var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	 module.ProductCategoriesWidget = module.ProductCategoriesWidget.extend({
        	
        	
        	renderElement: function(){
		    var self = this;
		    this._super();
		    var el_str  = openerp.qweb.render(this.template, {widget: this});
		    var el_node = document.createElement('div');
		        el_node.innerHTML = el_str;
		        el_node = el_node.childNodes[1];

		    if(this.el && this.el.parentNode){
		        this.el.parentNode.replaceChild(el_node,this.el);
		    }

		    this.el = el_node;

		    var hasimages = false;  //if none of the subcategories have images, we don't display buttons with icons
		    for(var i = 0; i < this.subcategories.length; i++){
		        if(this.subcategories[i].image){
		            hasimages = true;
		            break;
		        }
		    }

		    var list_container = el_node.querySelector('.category-list');
		    if (list_container) { 
		        if (!hasimages) {
		            list_container.classList.add('simple');
		        } else {
		            list_container.classList.remove('simple');
		        }
		        for(var i = 0, len = this.subcategories.length; i < len; i++){
		            list_container.appendChild(this.render_category(this.subcategories[i],hasimages));
		        };
		    }

		    var buttons = el_node.querySelectorAll('.js-category-switch');
		    for(var i = 0; i < buttons.length; i++){
		        buttons[i].addEventListener('click',this.switch_category_handler);
		    }
		    //yogesh
		    console.log("yogesh..............................",this.category);
		    if  (this.category['id'] == 0 || 'child_id' in this.category && this.category['child_id'].length > 0 ) 
		       {
		    	$('.content-row').addClass('oe_hidden');
		    	$('.layout-table').css('height','0%');
		    	}
		    else{
		    	$('.category-list').addClass('oe_hidden');
		    	$('.content-row').removeClass('oe_hidden');
		    	$('.layout-table').css('height','100%');
		    	}
		    	
		    var products = this.pos.db.get_product_by_category(this.category.id);
		    this.product_list_widget.set_product_list(products);
		  
		    
		    
		    this.el.querySelector('.searchbox input').addEventListener('keyup',this.search_handler);

		    this.el.querySelector('.search-clear').addEventListener('click',this.clear_search_handler);

		    if(this.pos.config.iface_vkeyboard && this.pos_widget.onscreen_keyboard){
		        this.pos_widget.onscreen_keyboard.connect($(this.el.querySelector('.searchbox input')));
		    }
		},
       	      });
       	      
     }
