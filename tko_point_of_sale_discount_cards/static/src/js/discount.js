L266
module.OrderWidget = module.OrderWidget.extend({
update_summary: function(){
    var order = this.pos.get('selectedOrder');
    var total     = order ? order.getTotalTaxIncluded() : 0;
    var taxes     = order ? total - order.getTotalTaxExcluded() : 0;
    var discount_id = self.$('#discount-card-select').val();
    var discount_promise;
    
    if (discount_id) {
        var discount_card = new module.PaymentScreenDiscountWidget(this, {});
        
        discount_promise = discount_card
        .fetch('pos.discount.cards',['type', 'value'],[['id','=', discount_id]])
        .then(function(discount)
        {
            var type =  discount[0].type;
            var value = discount[0].value;
            if (type === 'fi'){
                discount  = value;    
            }
            else{
                discount  = value + 100;
            }
            console.log("discount value.........................",value)
            return discount;
        });
    }
    else
    {
        discount_promise = Promise.resolve(0);
    }
    
    discount_promise
    .then(function (discount)
    {
        console.log("discount value fianl....................val",discount);
        this.el.querySelector('.summary .total > .value').textContent = this.format_currency(total);
        this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(taxes);
        this.el.querySelector('.summary .total .discount .value').textContent = this.format_currency(discount);
    }.bind(this));
},

});






module.Order = module.Order.extend({

    getTotalTaxIncluded: function() {
          
            var discount_val = self.$('#discount-card-select').val();
            var subtotal = (this.get('orderLines')).reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_with_tax();
            }), 0);
            var discount = 0.0;
            var total = 0.0
            if (discount_val)
                {
                    discount_data = discount_val.split(':')
                    discount_value = discount_data[1]
                    discount_type = discount_data[2]
                    if (discount_type === 'fi')
                        {
                            discount = discount_value;

                        }
                    else
                        {
                             discount = (subtotal * discount_value)/100;
                        }
                }
            total = subtotal - discount;
            console.log("getTotalTaxIncluded.................",total)
            return total;
            
        }
});













//compute discount of 

module.OrderWidget = module.OrderWidget.extend({
update_summary: function(){
this._super();
var order = this.pos.get('selectedOrder');
var total     = order ? order.getTotalTaxIncluded() : 0;
var taxes     = order ? total - order.getTotalTaxExcluded() : 0;
var discount_val = self.$('#discount-card-select').val();
var discount_promise;

if (discount_val) {
    var discount_card = new module.PaymentScreenDiscountWidget(this, {});
    discount_id = discount_val.split(':')[0]
    discount_promise = discount_card
    .fetch('pos.discount.cards',['type', 'value'],[['id','=', discount_id]])
    .then(function(discount)
    {
        var type =  discount[0].type;
        var value = discount[0].value;
        if (type === 'fi'){
            discount  = value;
        }
        else{
            discount  = (total * value) / 100;
        }
        return discount;
    });
}
else
{
    discount_promise = Promise.resolve(0);
}

discount_promise
.then(function (discount)
{
    this.el.querySelector('.summary .total > .value').textContent = this.format_currency(total - discount);
    this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(taxes);
    this.el.querySelector('.summary .total .discount .value').textContent = this.format_currency(-discount);
}.bind(this));
},

});
