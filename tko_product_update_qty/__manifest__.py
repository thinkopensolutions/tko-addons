# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{

    "name": "Improve, Update product qty wizard",
    "summary": "Simplifying Product Update Qty.",
    "category": "Website",
    "version": "1.0.0",
    "sequence": 1,
    "author": "TKO",
    "license": "Other proprietary",
    "website": "https://tko.tko-br.com",
    "depends": [
        'stock',
    ],
    "data": [
        'wizard/stock_change_product_qty_view.xml',
        'views/inventory_view.xml',
    ],
    "images": ['static/description/Banner.png'],
    "application": True,
    "installable": True,
    "auto_install": False,

}
