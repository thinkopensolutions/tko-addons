openerp.tko_l10n_br_point_of_sale_print_cupom_fiscal = function(instance){

    var module = instance.point_of_sale;
    tko_pos_print_receipt(instance,module);
    tko_pos_print_screens(instance,module);
    tko_pos_store_cnpj_cpf(instance,module);

    

};

