
from odoo import models, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit ='sale.order'

    @api.multi
    def set_delivery_line(self):

        # Remove delivery products from the sales order
        self._remove_delivery_line()

        for order in self:
            if order.state not in ('draft', 'sent'):
                raise UserError(_('You can add delivery price only on unconfirmed quotations.'))
            elif not order.carrier_id:
                raise UserError(_('No carrier set for this order.'))
            elif not order.delivery_rating_success:
                raise UserError(_('Please use "Check price" in order to compute a shipping price for this quotation.'))
            else:
                price_unit = order.carrier_id.rate_shipment(order)['price']
                # TODO check whether it is safe to use delivery_price here
                final_price = price_unit * (1.0 + (float(self.carrier_id.margin) / 100.0))
                # order._create_delivery_line(carrier, final_price)
                # set price in total_frete field and compute total again
                order.total_frete = final_price
                order.delivery_price = final_price
                order._amount_all()

        return True