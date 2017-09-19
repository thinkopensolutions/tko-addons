odoo.define('tko_purchase_requisition.generate_po', function (require) {
"use strict";

	var ListView = require('web.ListView');
	var Model = require('web.DataModel');
	var data = require('web.data');

	ListView.include({
		init: function() {
	        var self = this;
	        var active_id;
	        this._super.apply(this, arguments);
	        self.generate_po = function(event){
	        	event.stopImmediatePropagation();
	        	var url = window.location.href;
                if(url.match('active_id') && url.match('active_id')[0]){
                	var active_id = parseInt(/active_id=(\d+)/.exec(url)[1]);
                }
                if (active_id){
                	new Model('purchase.requisition').call('generate_po',[active_id])
                    .then(function(record){
                        if (record){
                        	new Model("ir.actions.actions").get_func("search_read")([['name', '=', 'Purchase Agreements']], ['id']).then(
                				function(action_id) {
                					if(action_id && action_id[0]){
                						var url1 = "/web#id="+parseInt(active_id)+"&view_type=form&model=purchase.requisition&action="+action_id[0].id;
                                    	window.open(url1, '_self');
                					}else{
                						alert("Record not found...");
                					}
                				});
                        }
                    });
                }else{
                	alert("Record id not found");
                }
	        };
		},
		load_list: function() {
			var res = this._super();
	        var self = this;
	        $('body').on('click', '.generate_po', self.generate_po);
			return res;
		},
	});
});
