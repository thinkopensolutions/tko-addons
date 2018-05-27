console.log("loading the file................");
odoo.define('tko_account_sign_up_br_details.cnpj_cpf', function (require) {
    "use strict";

    var ajax = require('web.ajax');

    function cnpj_cpf_mask(){
        // Mask Phone
        $('input[type=text][name=phone]').mask('(00) 00000-0000');
        // Mask CNPJ CPF
        var company = $('#radioCompany').prop('checked');
        $('input[type=text][name=cnpj_cpf]').text('');
        if (company){
            $('input[type=text][name=cnpj_cpf]').mask('00.000.000/0000-00');
            $('label[for=cnpj_cpf]').text('CNPJ')
        } else {
            $('input[type=text][name=cnpj_cpf]').mask('000.000.000-00');
            $('label[for=cnpj_cpf]').text('CPF')
        }

    };

    $(document).ready(function () {
        cnpj_cpf_mask();
        var SPMaskBehavior = function(val) {
            return val.replace(/\D/g, '').length === 11 ?
                '(00) 00000-0000' :
                '(00) 0000-00009';
        },
        spOptions = {
            onKeyPress: function(val, e, field, options) {
                field.mask(SPMaskBehavior.apply({},
                            arguments), options);
            }
        };


//        cnpj_cpf_mask();



        $('input[type=radio][name=company_type]').change(function() {
            console.log("Changed...................");
            cnpj_cpf_mask();
        });
    });
});
