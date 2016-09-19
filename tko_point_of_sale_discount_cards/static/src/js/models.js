function pos_discount_cards_model(instance, module){ //module is instance.point_of_sale
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    module.PosModel.prototype.models.filter(function (m)
     { return m.model === 'pos.session'; }).map(function (m) {
      return m.fields.push('discount_card_ids'),
      m;
       });

    // set allowed discount cards in pos
    module.PosModel.prototype.models.push(
            {
                model:  'pos.discount.cards',
                fields: ['name', 'type', 'value' , 'active' ],
                loaded: function(self,cards){
                    filterd_cards = []
                    // filter cards allowed in configuration
                    allowed_cards = self.pos_session.discount_card_ids;
                    _.filter(cards, function(card){
                        if (allowed_cards.indexOf(card.id)!== -1)
                        {
                            filterd_cards.push(card);
                        }

                    })
                    self.cards = filterd_cards;
                }
            }
    )
};
