$(document).ready(function() {
    $()
});

function tko_pos_print_screens(instance, module) { //module is instance.point_of_sale
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;




    module.PaymentScreenWidget = module.PaymentScreenWidget.extend({

        el: '.cnpj_input',

        events: _.extend({
            "keypress .cnpj_input": "keypressCnpjCpf",
            "keypress .dialog-prompt input": "keypressCnpjCpf",
            "click .cnpj_input": "clickCnpjCpf",
            "click #cnpj_cpf_btn": "clickCnpjCpf"
        }, module.PaymentScreenWidget.prototype.events),

        keypressCnpjCpf: function(e) {
            if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
                return false;
            }
        },

        clickCnpjCpf: function(e) {
            var cnpj_cpf = $(".cnpj_input").val().replace(/\D/g, '');
            smoke.prompt("CPF / CNPJ", function(e) {
                // if there is input
                if (e) {
                    //set value to field on parent form
                    $(".cnpj_input").val(e);

                    try{
                        var partners = self.pos.partners;
                        var partner = undefined;
                        for (i = 0; i < partners.length; i++) {
                            if (partners[i]["cnpj_cpf"] && partners[i]["cnpj_cpf"].replace(/\D/g, '') === e)
                                partner = partners[i];
                            self.pos.get('selectedOrder').set_client(partner);
                        }
                    }
                    catch (error){
                        var partners = self.posmodel.partners;
                        var partner = undefined;
                        for (i = 0; i < partners.length; i++) {
                            if (partners[i]["cnpj_cpf"] && partners[i]["cnpj_cpf"].replace(/\D/g, '') === e)
                                partner = partners[i];
                            self.posmodel.pos_widget.pos.get('selectedOrder').set_client(partner);
                        }

                    }


                    // if input is 12 digits long its supposed to be a CPF
                    if (e.length === 11) {
                        cpf = e.replace(/[^\d]+/g, '');
                        var numeros, digitos, soma, i, resultado, digitos_iguais;
                        digitos_iguais = 1;

                        for (i = 0; i < cpf.length - 1; i++)
                            if (cpf.charAt(i) != cpf.charAt(i + 1)) {
                                digitos_iguais = 0;
                                break;
                            }
                        if (!digitos_iguais) {
                            numeros = cpf.substring(0, 9);
                            digitos = cpf.substring(9);
                            soma = 0;
                            for (i = 10; i > 1; i--)
                                soma += numeros.charAt(10 - i) * i;
                            resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
                            if (resultado != digitos.charAt(0)) {
                                smoke.alert("Invalid CPF ", function(e) {
                                    $('#cnpj_cpf_btn').trigger('click');
                                });
                                return false;

                            }

                            numeros = cpf.substring(0, 10);
                            soma = 0;
                            for (i = 11; i > 1; i--)
                                soma += numeros.charAt(11 - i) * i;
                            resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
                            if (resultado != digitos.charAt(1)) {
                                smoke.alert("Invalid CPF", function(e) {
                                    $('#cnpj_cpf_btn').trigger('click');
                                });
                                return false;
                                return true;
                            }
                        } else {
                            smoke.alert("Invalid CPF", function(e) {
                                $('#cnpj_cpf_btn').trigger('click');
                                return false;
                            });
                        }
                    }


                    // if input is 12 digits long its supposed to be a CNPJ
                    else if (e.length === 14) {

                        //start CNPJ check

                        cnpj = e.replace(/[^\d]+/g, '');

                        // LINHA 10 - Elimina CNPJs invalidos conhecidos
                        if (cnpj == "00000000000000" ||
                            cnpj == "11111111111111" ||
                            cnpj == "22222222222222" ||
                            cnpj == "33333333333333" ||
                            cnpj == "44444444444444" ||
                            cnpj == "55555555555555" ||
                            cnpj == "66666666666666" ||
                            cnpj == "77777777777777" ||
                            cnpj == "88888888888888" ||
                            cnpj == "99999999999999") {
                            smoke.alert("Invalid CNPJ ", function(e) {
                                console.log("invalid cpf /cnpj")
                                $('#cnpj_cpf_btn').trigger('click');
                            });
                            return false; // LINHA 21
                        }


                        // Valida DVs LINHA 23 -
                        tamanho = cnpj.length - 2
                        numeros = cnpj.substring(0, tamanho);
                        digitos = cnpj.substring(tamanho);
                        soma = 0;
                        pos = tamanho - 7;
                        for (i = tamanho; i >= 1; i--) {
                            soma += numeros.charAt(tamanho - i) * pos--;
                            if (pos < 2)
                                pos = 9;
                        }
                        resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
                        if (resultado != digitos.charAt(0)) {
                            smoke.alert("Invalid CNPJ", function(e) {
                                console.log("invalid cpf /cnpj")
                                $('#cnpj_cpf_btn').trigger('click');
                            });
                            return false; // LINHA 21
                        }

                        tamanho = tamanho + 1;
                        numeros = cnpj.substring(0, tamanho);
                        soma = 0;
                        pos = tamanho - 7;
                        for (i = tamanho; i >= 1; i--) {
                            soma += numeros.charAt(tamanho - i) * pos--;
                            if (pos < 2)
                                pos = 9;
                        }
                        resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
                        if (resultado != digitos.charAt(1)) {
                            smoke.alert("Invalid CNPJ ", function(e) {
                                console.log("invalid cpf /cnpj")
                                $('#cnpj_cpf_btn').trigger('click');
                            });
                            return false; // LINHA 21
                        } // LINHA 49

                        return true; // LINHA 51


                        //End CNPJ check
                    }
                    // if input length is other than 12 or14 digits its wrong input
                    else {
                        smoke.alert("Invalid CPF / CNPJ", function(e) {
                            console.log("invalid cpf /cnpj")
                            $('#cnpj_cpf_btn').trigger('click');
                        });
                    }


                } else {
                    if (e) {
                        $(".cnpj_input").val(e);
                    } else {
                        $(".cnpj_input").val('');
                    }

                }
            }, {
                classname: "cnpj_input_dialog",
                value: cnpj_cpf
            });
        },


        //validate CPF

        verifica_cpf: function(cpf) {
            cpf = cpf.replace(/[^\d]+/g, '');
            var numeros, digitos, soma, i, resultado, digitos_iguais;
            digitos_iguais = 1;
            if (cpf.length < 11)
                return false;
            for (i = 0; i < cpf.length - 1; i++)
                if (cpf.charAt(i) != cpf.charAt(i + 1)) {
                    digitos_iguais = 0;
                    break;
                }
            if (!digitos_iguais) {
                numeros = cpf.substring(0, 9);
                digitos = cpf.substring(9);
                soma = 0;
                for (i = 10; i > 1; i--)
                    soma += numeros.charAt(10 - i) * i;
                resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
                if (resultado != digitos.charAt(0))
                    return false;
                numeros = cpf.substring(0, 10);
                soma = 0;
                for (i = 11; i > 1; i--)
                    soma += numeros.charAt(11 - i) * i;
                resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
                if (resultado != digitos.charAt(1))
                    return false;
                return true;
            } else
                return false;


        },


        //validate CNPJ

        verifica_cnpj: function(cnpj) {
            cnpj = cnpj.replace(/[^\d]+/g, '');
            if (cnpj == '') return false;
            if (cnpj.length != 14)
                return false;
            // LINHA 10 - Elimina CNPJs invalidos conhecidos
            if (cnpj == "00000000000000" ||
                cnpj == "11111111111111" ||
                cnpj == "22222222222222" ||
                cnpj == "33333333333333" ||
                cnpj == "44444444444444" ||
                cnpj == "55555555555555" ||
                cnpj == "66666666666666" ||
                cnpj == "77777777777777" ||
                cnpj == "88888888888888" ||
                cnpj == "99999999999999")
                return false; // LINHA 21

            // Valida DVs LINHA 23 -
            tamanho = cnpj.length - 2
            numeros = cnpj.substring(0, tamanho);
            digitos = cnpj.substring(tamanho);
            soma = 0;
            pos = tamanho - 7;
            for (i = tamanho; i >= 1; i--) {
                soma += numeros.charAt(tamanho - i) * pos--;
                if (pos < 2)
                    pos = 9;
            }
            resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
            if (resultado != digitos.charAt(0))
                return false;

            tamanho = tamanho + 1;
            numeros = cnpj.substring(0, tamanho);
            soma = 0;
            pos = tamanho - 7;
            for (i = tamanho; i >= 1; i--) {
                soma += numeros.charAt(tamanho - i) * pos--;
                if (pos < 2)
                    pos = 9;
            }
            resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
            if (resultado != digitos.charAt(1))
                return false; // LINHA 49

            return true; // LINHA 51
        },

        show: function() {
            this._super();
            var currentOrder = this.pos.get('selectedOrder');
            var cnpj_cpf = currentOrder.get_client_cnpj_cpf() || "";
            this.pos_widget.$(".cnpj_input").val(cnpj_cpf);

        },

        // inherit PosWidget to add print button in top right header 	
        validate_order: function(options) {
            //TODO convert confirm to fancy dialogue box
            //confirm only if it is set to ask in configurations

            var self = this;
            smoke.confirm("Do you confirm payment?", function(confirmed) {
                if (confirmed) {

                    options = options || {};

                    var currentOrder = self.pos.get('selectedOrder');

                    if (currentOrder.get('orderLines').models.length === 0) {
                        self.pos_widget.screen_selector.show_popup('error', {
                            'message': _t('Empty Order'),
                            'comment': _t('There must be at least one product in your order before it can be validated'),
                        });
                        return;
                    }

                    var plines = currentOrder.get('paymentLines').models;
                    for (var i = 0; i < plines.length; i++) {
                        if (plines[i].get_type() === 'bank' && plines[i].get_amount() < 0) {
                            self.pos_widget.screen_selector.show_popup('error', {
                                'message': _t('Negative Bank Payment'),
                                'comment': _t('You cannot have a negative amount in a Bank payment. Use a cash payment method to return money to the customer.'),
                            });
                            return;
                        }
                    }

                    if (!self.is_paid()) {
                        return;
                    }

                    //get and validate CNPJ/CPF
                    var payment_cnpj_cpf = self.pos_widget.$(".cnpj_input").val().replace(/\D/g, '');;
                    //validate cpf if value is given

                    if (payment_cnpj_cpf) {
                        validator_cpf = self.verifica_cpf(payment_cnpj_cpf);

                        //if cpf is not validated , validate cnpj

                        if (!validator_cpf) {
                            validator_cnpj = self.verifica_cnpj(payment_cnpj_cpf);

                            //invalid cpf / cnpj
                            if (!validator_cnpj) {
                                self.pos_widget.screen_selector.show_popup('error', {
                                    'message': _t('Invalid CPF /CNPJ'),
                                    'comment': _t('Please fill correct CPF /CNPJ'),
                                });
                                return;

                            }
                        }


                    };




                    // The exact amount must be paid if there is no cash payment method defined.
                    if (Math.abs(currentOrder.getTotalTaxIncluded() - currentOrder.getPaidTotal()) > 0.00001) {
                        var cash = false;
                        for (var i = 0; i < self.pos.cashregisters.length; i++) {
                            cash = cash || (self.pos.cashregisters[i].journal.type === 'cash');
                        }
                        if (!cash) {
                            self.pos_widget.screen_selector.show_popup('error', {
                                message: _t('Cannot return change without a cash payment method'),
                                comment: _t('There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'),
                            });
                            return;
                        }
                    }

                    if (self.pos.config.iface_cashdrawer) {
                        self.pos.proxy.open_cashbox();
                    }

                    if (options.invoice) {
                        // deactivate the validation button while we try to send the order
                        self.pos_widget.action_bar.set_button_disabled('validation', true);
                        self.pos_widget.action_bar.set_button_disabled('invoice', true);

                        var invoiced = self.pos.push_and_invoice_order(currentOrder);

                        invoiced.fail(function(error) {
                            if (error === 'error-no-client') {
                                self.pos_widget.screen_selector.show_popup('error', {
                                    message: _t('An anonymous order cannot be invoiced'),
                                    comment: _t('Please select a client for this order. This can be done by clicking the order tab'),
                                });
                            } else {
                                self.pos_widget.screen_selector.show_popup('error', {
                                    message: _t('The order could not be sent'),
                                    comment: _t('Check your internet connection and try again.'),
                                });
                            }
                            self.pos_widget.action_bar.set_button_disabled('validation', false);
                            self.pos_widget.action_bar.set_button_disabled('invoice', false);
                        });

                        invoiced.done(function() {
                            self.pos_widget.action_bar.set_button_disabled('validation', false);
                            self.pos_widget.action_bar.set_button_disabled('invoice', false);
                            self.pos.get('selectedOrder').destroy();
                        });

                    } else {
                        // get cnpj_cpf form screen


                        // update cnpj_cpf in order
                        currentOrder.attributes.cnpj_cpf = payment_cnpj_cpf
                        self.pos.push_order(currentOrder)


                        // don't check for proxy, redirect to new order always
                        //if(this.pos.config.iface_print_via_proxy){
                        var receipt = currentOrder.export_for_printing();

                        self.pos.proxy.print_receipt(QWeb.render('XmlReceipt', {
                            receipt: receipt,
                            widget: self,
                        }));


                        var receipt = currentOrder.export_for_printing();


                        //data to print

                        var pos_data = currentOrder.export_for_printing();

                        // get current config, it will remain same over payment lines
                        var config_id = currentOrder.pos.config.id;
                        // filter fiscal codes of current session
                        var fiscal_codes = self.pos.fiscal_codes.filter(function(m) {
                            return m.config_id[0] === config_id;
                        });
                        // default fiscal code
                        var fiscal_code = self.pos.config.default_fiscal_code;
                        // make array of payment methods
                        payment_methods = []
                        payment_lines = currentOrder.get('paymentLines').models
                            // iterate over payment lines
                        for (i = 0; i < currentOrder.get('paymentLines').models.length; i++) {
                            var amount = payment_lines[i].amount
                                // get jouranal of current payment line
                            var jouranl_id = payment_lines[i].cashregister.journal.id
                            if (fiscal_codes.length > 0) {
                                for (j = 0; j < fiscal_codes.length; j++) {
                                    // get config and journal from fiscal codes
                                    fiscal_config_id = fiscal_codes[j].config_id[0];
                                    fiscal_journal_id = fiscal_codes[j].journal_id[0];
                                    // search for matching jouanl and config, if found append in array
                                    if (jouranl_id === fiscal_journal_id && config_id === fiscal_config_id && amount > 0) {
                                        payment_methods.push({
                                            "payment_method_index": String(fiscal_codes[j].fiscal_code) || String(fiscal_code),
                                            "paid_value": Number(parseFloat(amount).toFixed(2))
                                        })
                                    }

                                }

                            }
                        }
                        var orderlines = pos_data.orderlines;
                        var order = self.pos.get('selectedOrder');
                        var orderlines_disc = order.get('orderLines').models;
                        var itemlines = [];

                        for (i = 0; i < orderlines.length; i++) {
                            var aliquotaICMS = 'I';
                            var fixed_discount = orderlines_disc[i].discount
                            var tax_code_id = orderlines[i].icms_tax_code;
                            var icms_tax_value = orderlines[i].icms_tax_value;
                            if (icms_tax_value === 0.0){
                                tax_codes = self.pos.tax_codes;
                                tax_code = _.filter(tax_codes, function(tax_code){
                                    return tax_code.id  === tax_code_id;
                                })
                                if (tax_code.length > 0){
                                    aliquotaICMS = tax_code[0].pos_fiscal_code
                                }

                            }
                            else{
                                aliquotaICMS = icms_tax_value.toString() + 'T'
                            }
                            if (orderlines[i].quantity && orderlines[i].price_display) {
                                itemlines.push({
                                    "codigo_item": orderlines_disc[i].default_code || "000",
                                    "aliquotaICMS": aliquotaICMS,
                                    "descricao": orderlines[i].product_name || "",
                                    "unidade": orderlines[i].unit_name || 0,
                                    "tipoDescontoAcrescimo": "$",
                                    "quantidade": orderlines[i].quantity || 0,
                                    "valor_unitario": orderlines[i].price || 0.0,
                                    "percentualDesconto": orderlines_disc[i].discount_type === 'fi' ? fixed_discount : Number((parseFloat(orderlines_disc[i].quantity * orderlines_disc[i].price * orderlines_disc[i].discount) / 100).toFixed(2)) || 0.0,
                                    "codDepartamento": 3,
                                    "cfop_code": orderlines[i].cfop_code || ""

                                });
                            }
                        };

                        //currentOrder.attributes.paymentLines.models
                        vendedor = ""
                        try {
                            // pos_cashier module creates this field
                            vendedor = order.pos.cashier.name
                        } catch (err) {
                            vendedor = order.pos.user.name
                        }
                        // get cupom reference based on company config
                        var order_reference = ''
                        if (self.pos.company.order_reference === 'uid'){
                        	order_reference = String(currentOrder.uid).replace(/\D/g, '')
                        }
                        else{
                        	order_reference = currentOrder.sequence_number
                        }
                        json_data = {
                                "id": order_reference || 0,
                                "nome": currentOrder.get_client_name() || "NAO OBTIDO",
                                "cpf_cnpj": payment_cnpj_cpf || "",
                                "endereco_completo": currentOrder.get_client_address() || "NAO OBTIDO",
                                "itensCompra": itemlines,
                                "purchase_discount": Number(parseFloat(order.getDiscountCard()).toFixed(2)),
                                "average_federal_tax": self.pos.company.average_federal_tax || 0.0,
                                "average_state_tax": self.pos.company.average_state_tax || 0.0,
                                "payments": payment_methods,
                                "vendedor": vendedor,
                            }
                            //"unique_id" : order.uid

                        //send data to fiscal printer only if total of order is greater than 0
                        //open drawer & fiscal print 
                        try {
                            if (itemlines.length && currentOrder.getTotalTaxIncluded() > 0) {
                            	appECF.abrirGaveta();
                                appECF.imprimirCupom(JSON.stringify(json_data));
                            }

                        } catch (error) {
                            console.log(json_data)
                            //smoke.alert("Please check if applet is loaded, could not call appECF.imprimirCupom()")
                        }

                        //kitchen print
                        self.pos_widget.screen_selector.set_current_screen(self.next_screen);
                        //destroy order
                        self.pos.get('selectedOrder').destroy(); //finish order and go back to scan screen

                    }



                    // hide onscreen (iOS) keyboard 
                    setTimeout(function() {
                        document.activeElement.blur();
                        $("input").blur();
                    }, 250);
                } // end of if

            });


        },

    });
};
