odoo.define('tko_eradicate_create_and_edit.form_common', function (require) {
"use strict";

    var form_common = require('web.form_common');
    var utils = require('web.utils');

    form_common.CompletionFieldMixin.init = function() {
        this.limit = 7;
        this.orderer = new utils.DropMisordered();
        this.can_create = false;
        this.can_write = this.node.attrs.can_write || true;
    }

});