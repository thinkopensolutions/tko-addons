odoo.define('tko_coexiste_br_account.reconciliationa', function (require) {
"use strict";

    var reconciliation = require('account.reconciliation');

    reconciliation.abstractReconciliation.include({
        init: function(parent, context) {
            this._super(parent, context);
            this.create_form_fields['analytic_account_id']= {
                id: "analytic_account_id",
                index: 20,
                corresponding_property: "analytic_account_id",
                label: _t("Analytic Acc."),
                required: false,
                group:"analytic.group_analytic_accounting",
                constructor: FieldMany2One,
                field_properties: {
                    relation: "account.analytic.account",
                    string: _t("Analytic Acc."),
                    type: "many2one",
                },
            }


        },
    });
});
