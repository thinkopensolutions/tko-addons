odoo.define('tko_coexiste_br_account.reconciliationa', function (require) {
"use strict";
    var core = require('web.core');
    var _t = core._t;
    var reconciliation = require('account.reconciliation');
    var FieldMany2One = core.form_widget_registry.get('many2one');

    reconciliation.abstractReconciliation.include({
        init: function(parent, context) {
            this._super(parent, context);
            var self = this;
            this.create_form_fields['expense_type_id']= {
                id: "expense_type_id",
                index: 25,
                corresponding_property: "expense_type_id",
                label: _t("Expense Type"),
                required: false,
                group:"analytic.group_analytic_accounting",
                constructor: FieldMany2One,
                field_properties: {
                    relation: "account.expense.type",
                    string: _t("Expense Type"),
                    type: "many2one",
                },
            }


        },
    });
});
