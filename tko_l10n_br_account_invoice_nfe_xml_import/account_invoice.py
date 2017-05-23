# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
import xml.etree.ElementTree as ET

from openerp import models, fields, api, _
from openerp.exceptions import Warning

_logger = logging.getLogger(__name__)


class accountInvoice(models.Model):
    _inherit = 'account.invoice'

    xml_data = fields.Text(string='XML', copy=False)
    # nfe_access_key is created in l10n_br_account_product, we do not want to make module dependent on l10n_br_account_product so creating field in this module
    nfe_access_key = fields.Char('Chave de Acesso NFE', size=44, readonly=True, states={'draft': [('readonly', False)]},
                                 copy=False)

    @api.one
    def import_nfe_xml(self):

        def get_partner(cnpj_cpf, name, is_company):
            partner = self.env['res.partner']
            if cnpj_cpf:
                if len(cnpj_cpf) == 14:
                    cnpj_cpf = cnpj_cpf[0:2] + '.' + cnpj_cpf[2:5] + '.' + cnpj_cpf[5:8] + '/' + cnpj_cpf[
                                                                                                 8:12] + '-' + cnpj_cpf[
                                                                                                               12:15]
                partner = self.env['res.partner'].search([('cnpj_cpf', '=', cnpj_cpf)], limit=1)
            if not len(partner) and name:
                partner = self.env['res.partner'].search([('name', '=', name)], limit=1)
                if not len(partner):
                    _logger.info(_("Supplier %s with CNPJ %s not found in database") % (supplier_name, supplier_cnpj))
                    _logger.info(_("Creating supplier %s") % (supplier_name))
                    partner = self.env['res.partner'].create({
                        'name': name,
                        'is_company': True,
                        'cnpj_cpf': cnpj_cpf,
                        'type': 'contact'})
            return partner

        if self.xml_data:
            xml = self.xml_data.encode('utf-8')
            root = ET.fromstring(xml)
            root.findall("./country/neighbor")
            # search supplier with cnpj_cpf if not found them with name
            supplier = root.find('.//{http://www.portalfiscal.inf.br/nfe}emit')
            supplier_cnpj = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}CNPJ').text
            supplier_name = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}xNome').text
            partner = get_partner(supplier_cnpj, supplier_name, True)

            # NFe Number
            nfe_number = root.find('.//{http://www.portalfiscal.inf.br/nfe}nNF').text
            nfe_access_key = root.find('.//{http://www.portalfiscal.inf.br/nfe}chNFe').text

            # create invoice
            inv_dict = {
                'partner_id': partner.id,
                'account_id': partner.property_account_payable.id,
                'supplier_invoice_number': nfe_number,
                'nfe_access_key': nfe_access_key,
                'type': 'in_invoice',
            }

            invoice = self.env['account.invoice'].create(inv_dict)
            # find all products
            # uom  : uCom
            for product in root.findall('.//{http://www.portalfiscal.inf.br/nfe}prod'):
                product_name = product.find('.//{http://www.portalfiscal.inf.br/nfe}xProd').text
                product_code = product.find('.//{http://www.portalfiscal.inf.br/nfe}cProd').text
                product_uom = product.find('.//{http://www.portalfiscal.inf.br/nfe}uCom').text
                product_qty = product.find('.//{http://www.portalfiscal.inf.br/nfe}qTrib').text
                unit_price = product.find('.//{http://www.portalfiscal.inf.br/nfe}vUnTrib').text
                uom = self.env['product.uom'].search([('name', '=', product_uom)], limit=1)

                if not len(uom):
                    raise Warning(_("UoM %s not found in database" % product_uom))
                # search product in product_supplierinfo

                productinfo = self.env['product.supplierinfo'].search(
                    [('name', '=', partner.id), ('product_code', '=', product_code)], limit=1)
                if len(productinfo):
                    product_template = productinfo.product_tmpl_id
                else:
                    product_template = self.env['product.template'].search([('name', '=', product_name)], limit=1)
                    if not len(product_template):
                        product_template = self.env['product.template'].create({'name': product_name,
                                                                                'uom_id': uom.id,
                                                                                'uom_po_id': uom.id,
                                                                                'type': 'product',
                                                                                })
                    self.env['product.supplierinfo'].create({'name': partner.id,
                                                             'product_code': product_code,
                                                             'product_tmpl_id': product_template.id,
                                                             })
                # search product based on product template, it will be selected in invoice line
                product = self.env['product.product'].search([('product_tmpl_id', '=', product_template.id)], limit=1)
                if not len(product):
                    raise Warning(_("Product %s not found in database" % product_template.name))

                self.env['account.invoice.line'].create({'product_id': product.id,
                                                         'invoice_id': invoice.id,
                                                         'name': product_name,
                                                         'quantity': product_qty,
                                                         'price_unit': unit_price,
                                                         })
