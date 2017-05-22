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

import xml.etree.ElementTree as ET
from openerp import fields, models, api, _
from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)


class poline_info(models.TransientModel):
    _name = 'poline.info'

    product_name = fields.Char(u'Descrição do Produto')
    product_default_code = fields.Char(u'Referência Interna')
    nfe_default_code = fields.Char(u'NFe Referência Interna')
    supplier_product_name = fields.Char(u'Descrição do Produto do Fornecador')
    nfe_product_name = fields.Char('NFe Product Name')
    product_qty = fields.Float('Qty')
    nfe_product_qty = fields.Float('NFe Qty')
    product_uom = fields.Many2one('product.uom', 'UoM')
    nfe_product_uom = fields.Many2one('product.uom', 'NFe UoM')
    unit_price = fields.Float('Unit Price')
    nfe_unit_price = fields.Float('NFe Unit Price')
    product_ncm = fields.Char('NCM')
    xml_ncm = fields.Char('NFe NCM')
    # tax_ids = fields.Many2many('account.tax', 'tax_poline_info_wizrd_rel', 'tax_id', 'wizard_id', 'Taxes')
    wizard_id = fields.Many2one('nfe.xml.validate', 'Wizard', delete='cascade')
    ignore = fields.Boolean(u"Ignore")


class nfe_xml_validate(models.TransientModel):
    _name = 'nfe.xml.validate'

    xml_file = fields.Binary('File', )
    xml_file_name = fields.Char("File Name", readonly=True)
    po_line_info = fields.One2many('poline.info', 'wizard_id', 'PO Lines')
    supplier_nfe = fields.Many2one('res.partner', 'Supplier NFe', readonly=True)
    supplier_po = fields.Many2one('res.partner', 'Supplier PO', readonly=True)
    partner_legal_name = fields.Char(u'Razão Social', readonly=True)
    xml_legal_name = fields.Char(u'NFe Razão Social', readonly=True)
    partner_cnpj_cpf = fields.Char(u'CNPJ', readonly=True)
    xml_cnpj_cpf = fields.Char(u'NFe CNPJ', readonly=True)
    partner_ie = fields.Char(u'IE', readonly=True)
    xml_ie = fields.Char(u'XML IE', readonly=True)

    @api.multi
    def validate_nfe_xml(self):

        # Extract Partner
        def get_partner(supplier):
            cnpj_cpf = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}CNPJ').text
            name = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}xNome').text
            partner = "No Supplier %s found with CNPJ %s" % (name, cnpj_cpf)
            partner_obj = self.env['res.partner']
            if cnpj_cpf:
                if len(cnpj_cpf) == 14:
                    cnpj_cpf = cnpj_cpf[0:2] + '.' + cnpj_cpf[2:5] + '.' + cnpj_cpf[5:8] + '/' + cnpj_cpf[
                                                                                                 8:12] + '-' + cnpj_cpf[
                                                                                                               12:15]
                    partner = partner_obj.search([('cnpj_cpf', '=', cnpj_cpf)], limit=1)
            if not len(partner):
                raise Warning(u"Supplier not found with CNPJ : %s" % cnpj_cpf)
            return partner

        def get_product_name_default_code(supplier, product):
            product_name = False
            default_code = False
            for line in product.seller_ids:
                if line.name == supplier and line.product_name:
                    product_name = line.product_name
                    default_code = line.product_code
                    break;
            return product_name, default_code

        po_lines = []
        computed_lines = []
        # delete lines
        self.po_line_info.unlink()
        active_id = self.env.context.get('active_id', False)
        order = self.env['purchase.order'].browse(active_id)
        po_lines_dict = {}
        for line in order.order_line:
            supplier_proudct_name = line.supplier_product_name or line.product_id.name
            supplier_default_code = line.supplier_product_code
            # line.product_id.name
            po_lines_dict.update({
                supplier_proudct_name: (
                                        line.product_qty,
                                        line.price_unit,
                                        line.product_uom.id,
                                        line.product_id.name,
                                        supplier_default_code)
            })
        # read file
        xml = self.xml_file.decode('base64')
        root = ET.fromstring(xml)

        # search supplier with cnpj_cpf
        supplier = root.find('.//{http://www.portalfiscal.inf.br/nfe}emit')
        partner = get_partner(supplier)
        xml_cnpj = root.find('.//{http://www.portalfiscal.inf.br/nfe}CNPJ').text
        xml_ie = root.find('.//{http://www.portalfiscal.inf.br/nfe}IE').text
        xml_legal_name = root.find('.//{http://www.portalfiscal.inf.br/nfe}xNome').text

        for det in root.findall('.//{http://www.portalfiscal.inf.br/nfe}det'):
            # match no of products in XML and PO
            nfe_product_name = det.find('.//{http://www.portalfiscal.inf.br/nfe}xProd').text
            nfe_product_code = det.find('.//{http://www.portalfiscal.inf.br/nfe}cProd').text
            nfe_product_uom = det.find('.//{http://www.portalfiscal.inf.br/nfe}uCom').text
            nfe_product_qty = det.find('.//{http://www.portalfiscal.inf.br/nfe}qTrib').text
            nfe_unit_price = det.find('.//{http://www.portalfiscal.inf.br/nfe}vUnTrib').text
            nfe_product_taxes = det.findall('.//{http://www.portalfiscal.inf.br/nfe}imposto/')
            nfe_discount_value = det.find('.//{http://www.portalfiscal.inf.br/nfe}vDesc')
            nfe_product_value = det.find('.//{http://www.portalfiscal.inf.br/nfe}vProd')
            nfe_uom = self.env['product.uom'].search([('name', 'ilike', nfe_product_uom)], limit=1)
            if not len(nfe_uom):
                raise Warning("Unit of measure %s not found" % nfe_product_uom)
            product_cfop = det.find('.//{http://www.portalfiscal.inf.br/nfe}CFOP').text
            product_ncm = det.find('.//{http://www.portalfiscal.inf.br/nfe}NCM').text
            # if line found in PO
            pol_product_name = pol_product_uom = pol_supplier_product_name = pol_default_code = False
            pol_product_qty = pol_unit_price = 0.0
            # if product from NFe matches in PO lines
            if nfe_product_name in po_lines_dict.keys():
                pol_supplier_product_name = nfe_product_name
                pol_product_qty = po_lines_dict[nfe_product_name][0]
                pol_unit_price = po_lines_dict[nfe_product_name][1]
                pol_product_uom = po_lines_dict[nfe_product_name][2]
                pol_product_name = po_lines_dict[nfe_product_name][3]
                pol_default_code = po_lines_dict[nfe_product_name][4]
                # delete key from dict
                po_lines_dict.pop(nfe_product_name)

            # create lines from Nfe
            computed_lines.append((0, 0, {
                'supplier_product_name': pol_supplier_product_name,
                'product_default_code': pol_default_code,
                'product_name': pol_product_name,
                'product_qty': pol_product_qty,
                'unit_price': pol_unit_price,
                'product_uom': pol_product_uom,
                'nfe_product_name': nfe_product_name,
                'nfe_product_qty': nfe_product_qty,
                'nfe_unit_price': nfe_unit_price,
                'nfe_product_uom': nfe_uom.id,
                'nfe_default_code': nfe_product_code,

            }))
        # create purchase order lines
        for key, values in po_lines_dict.iteritems():
            computed_lines.append((0, 0, {
                'nfe_product_name': False,
                'nfe_product_qty': False,
                'nfe_unit_price': False,
                'nfe_product_uom': False,
                'supplier_product_name': key,
                'product_qty': values[0],
                'unit_price': values[1],
                'product_uom': values[2],
                'product_name': values[3],
            }))

        self.write({'po_line_info': computed_lines,
                    'supplier_po': order.partner_id.id,
                    'supplier_nfe': partner.id,
                    'partner_legal_name': partner.legal_name,
                    'partner_cnpj_cpf': partner.cnpj_cpf,
                    'partner_ie': partner.inscr_est,
                    'xml_legal_name': xml_legal_name,
                    'xml_cnpj_cpf': xml_cnpj,
                    'xml_ie': xml_ie,

                    })

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'nfe.xml.validate',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    # validate lines before approve order
    def validate_lines(self):
        if self.supplier_nfe != self.supplier_po:
            raise Warning(_(u'Supplier Mismatch'))
        partner_cnpj_cpf = xml_cnpj_cpf = ''
        if self.xml_cnpj_cpf:
            xml_cnpj_cpf = str(self.xml_cnpj_cpf)
        if self.partner_cnpj_cpf:
            partner_cnpj_cpf = str(self.partner_cnpj_cpf)
        if int(filter(str.isdigit, partner_cnpj_cpf)) != int(filter(str.isdigit, xml_cnpj_cpf)):
            raise Warning(_(u'CNPJ Mismatch'))
        if self.partner_legal_name != self.xml_legal_name:
            raise Warning(_(u'Razão Social Mismatch'))
        if self.partner_ie != self.xml_ie:
            raise Warning(_(u'IE Mismatch'))
        for line in self.po_line_info:
            if not line.ignore:
                if line.supplier_product_name != line.nfe_product_name:
                    raise Warning(u"Descrição do Produto para produto %s" % line.nfe_product_name)
                if line.product_default_code != line.nfe_default_code:
                    raise Warning(u"Referência Interna mismatch para produto %s" % line.nfe_product_name)
                if line.product_qty != line.nfe_product_qty:
                    raise Warning("Prodct %s quantity mismatch" % line.nfe_product_name)
                if line.product_uom != line.nfe_product_uom:
                    raise Warning("Prodct %s UoM mismatch" % line.nfe_product_name)
        return True

    # Approve Order
    @api.multi
    def approve_purchase_order(self):
        self.validate_lines()
        active_id = self.env.context.get('active_id', False)
        if active_id:
            order = self.env['purchase.order'].browse(active_id)
            return order.signal_workflow('purchase_approve')
        return True

    # Cancel Order
    @api.multi
    def cancel_purchase_order(self):
        active_id = self.env.context.get('active_id', False)
        if active_id:
            order = self.env['purchase.order'].browse(active_id)
            return order.signal_workflow('purchase_cancel')
        return True
