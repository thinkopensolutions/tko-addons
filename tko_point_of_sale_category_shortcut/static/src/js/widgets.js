function pos_category_short_cut_widget(instance, module){ //module is instance.point_of_sale
        var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	
	
    //Create widget for shortcut categories 
    module.ProductCategoriesShortCutWidget = module.PosBaseWidget.extend({
        template: 'ProductCategoriesShortCutWidget',
        init: function(parent, options){
            var self = this;
            this._super(parent,options);
            this.product_type = options.product_type || 'all';  // 'all' | 'weightable'
            this.onlyWeightable = options.onlyWeightable || false;
            this.category = this.pos.root_category;
            this.breadcrumb = [];
            this.subcategories = [];
            this.product_list_widget = options.product_list_widget || null;
            this.category_cache = new module.DomCache();
            this.set_category();
            
            this.switch_category_handler = function(event){
                self.set_category(self.pos.db.get_category_by_id(Number(this.dataset['categoryId'])));
                self.renderElement();
            };
           
        },

        // changes the category. if undefined, sets to root category
        set_category : function(category){
            var db = this.pos.db;
            if(!category){
                this.category = db.get_category_by_id(db.root_category_id);
            }else{
                this.category = category;
            }
            
            this.breadcrumb = [];
            var ancestors_ids = db.get_category_ancestors_ids(this.category.id);
            for(var i = 1; i < ancestors_ids.length; i++){
                this.breadcrumb.push(db.get_category_by_id(ancestors_ids[i]));
            }
            if(this.category.id !== db.root_category_id){
                this.breadcrumb.push(this.category);
            }
            this.subcategories = db.get_category_by_id(db.get_category_childs_ids(0));
            //get all categories
            var allcategories = db.category_by_id;
            var shortcutcategories = [];
            _.each(allcategories,function(categ){
                if (categ.pos_shortcut){
                    shortcutcategories.push(categ)
                    };
            });

           this.subcategories = shortcutcategories;
           
            
        },

        get_image_url: function(category){
            return window.location.origin + '/web/binary/image?model=pos.category&field=image_medium&id='+category.id;
        },

        render_category: function( category, with_image ){
            var cached = this.category_cache.get_node(category.id);
            if(!cached){
                if(with_image){
                    var image_url = this.get_image_url(category);
                    var category_html = QWeb.render('CategoryButton',{ 
                            widget:  this, 
                            category: category, 
                            image_url: this.get_image_url(category),
                        });
                        category_html = _.str.trim(category_html);
                    var category_node = document.createElement('div');
                        category_node.innerHTML = category_html;
                        category_node = category_node.childNodes[0];
                }else{
                    var category_html = QWeb.render('CategorySimpleButton',{ 
                            widget:  this, 
                            category: category, 
                        });
                        category_html = _.str.trim(category_html);
                    var category_node = document.createElement('div');
                        category_node.innerHTML = category_html;
                        category_node = category_node.childNodes[0];
                }
                this.category_cache.cache_node(category.id,category_node);
                return category_node;
            }
            return cached; 
        },

        replace: function($target){
            this.renderElement();
            var target = $target[0];
            target.parentNode.replaceChild(this.el,target);
        },

        renderElement: function(){
            var self = this;

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

            var list_container = el_node.querySelector('.category-list-shortcut');
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

            var products = this.pos.db.get_product_by_category(this.category.id);
            this.product_list_widget.set_product_list(products);
	    
        },
        
        // resets the current category to the root category
        reset_category: function(){
            this.set_category();
            this.renderElement();
        },

        
    });
	
	
	
	
	
	
	// hide shortcut categories unless it is not leaf category
	var ProductCategoriesWidgetsuper = module.ProductCategoriesWidget;
	module.ProductCategoriesWidget = module.ProductCategoriesWidget.extend({
        	
        	
        	renderElement: function(){
		    var self = this;
		    this._super();
		    
		    if  (this.category['id'] == 0 || 'child_id' in this.category && this.category['child_id'].length > 0 ) 
		       {
		    	$('.footer-row').addClass('oe_hidden');
		    	$('.layout-table').css('height','0%');
		    	}
		    else{
		    	$('.footer-row').removeClass('oe_hidden');
		    	$('.layout-table').css('height','100%');
		    	}
		    	
		   
		    
		    
		},
       	      });
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	 	      
     }
