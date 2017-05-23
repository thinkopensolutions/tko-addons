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

from openerp import fields, models, api, _
from openerp.exceptions import Warning

_logger = logging.getLogger(__name__)


class nfeAttachment(models.TransientModel):
    _name = 'nfe.attachment'
    _inherits = {'ir.attachment': 'nfe_attachment_id'}

    nfe_attachment_id = fields.Many2one('ir.attachment', 'Attachment', ondelete="cascade", required=True)
    wizard_id = fields.Many2one('nfe.attachment.wizard', 'Wizard', ondelete="cascade", copy=False)
    state = fields.Selection([('e', 'Error'), ('i', 'Draft'), ('d', 'Done')], string='state', default='i')
    error_message = fields.Text('Message')

    @api.multi
    def unlink(self):
        for record in self:
            attachment = record.nfe_attachment_id
            res = super(nfeAttachment, record).unlink()
            attachment.unlink()
            return res


class nfeAttachmentWizard(models.TransientModel):
    _name = 'nfe.attachment.wizard'

    name = fields.Char('Name')
    attachment_ids = fields.One2many('nfe.attachment', 'wizard_id', string='Attachments')
    create_taxes = fields.Boolean("Create Taxes", help="If this field is set, taxes not found in db will be created")
    active_model = fields.Char('Active Model', copy=False)
    active_id = fields.Integer('Active ID', copy=False)
    invoice_type = fields.Selection([('c', 'Client'), ('s', 'Supplier')], default='s', string='Invoice Type')

    @api.model
    def default_get(self, fields_list):
        res = super(nfeAttachmentWizard, self).default_get(fields_list)
        context = self._context
        if context.get('active_model') == 'nfe.attachment.wizard':
            res['active_model'] = self.active_model
            res['active_id'] = self.active_id
        elif context.get('active_model') == 'stock.picking':
            picking = self.env['stock.picking'].browse(context.get('active_id'))
            if picking.origin:
                po = self.env['purchase.order'].search([('name', '=', picking.origin)])
                if not len(po):
                    raise Warning("No Purchase order found")
                elif len(po) > 1:
                    raise Warning("Multiple Purchase orders found")
                else:
                    res['active_model'] = 'purchase.order'
                    res['active_id'] = po.id
        else:
            res['active_model'] = context.get('active_model', False)
            res['active_id'] = context.get('active_id', False)
        return res

    @api.multi
    def import_nfe_xml(self):
        po = False
        if self.active_model == 'purchase.order' and self.active_id:
            po = self.env['purchase.order'].browse(self.active_id)
        for attachment in self.attachment_ids:
            def get_cfop(cfop_code):
                result = {'id': False, 'error_message': 'CFOP %s not found' % cfop_code}
                if cfop_code:
                    cfop = self.env['l10n_br_account_product.cfop'].search([('code', '=', cfop_code)], limit=1)
                    if len(cfop):
                        result = {'id': cfop.id, 'error_message': ''}
                    return result
                else:
                    return result

            def get_ncm(ncm_code):
                result = {'id': False, 'error_message': 'NCM %s not found' % ncm_code}
                if ncm_code:
                    # read ncm using sql query because ncm codes have dots in database
                    query = "select id from account_product_fiscal_classification where replace(name,'.','')='" + str(
                        ncm_code) + "'";
                    self._cr.execute(query)
                    ncm_id = self._cr.fetchone()
                    if ncm_id and len(ncm_id):
                        result = {'id': ncm_id[0], 'error_message': ''}
                    return result
                else:
                    return result

            def get_partner(supplier):
                cnpj_cpf = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}CNPJ').text
                name = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}xNome').text
                state_code = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}UF').text
                state_id = False
                country_id = False
                city_id = False
                # search state
                if state_code:
                    state = self.env['res.country.state'].search([('code', '=ilike', state_code)], limit=1)
                    if len(state):
                        state_id = state.id
                if po and po.partner_id.name != name or po and po.partner_id.state_id.code != state_code:
                    raise Warning(_("Supplier mismatch \
                    \n PO Supplier: %s, State Code: %s \
                    \n XML Supplier: %s, State Code: %s" % (
                    po.partner_id.name, po.partner_id.state_id.code, name, state_code)))
                partner = self.env['res.partner']
                if cnpj_cpf:
                    if len(cnpj_cpf) == 14:
                        cnpj_cpf = cnpj_cpf[0:2] + '.' + cnpj_cpf[2:5] + '.' + cnpj_cpf[5:8] + '/' + cnpj_cpf[
                                                                                                     8:12] + '-' + cnpj_cpf[
                                                                                                                   12:15]
                    partner = self.env['res.partner'].search([('cnpj_cpf', '=', cnpj_cpf)], limit=1)
                if not len(partner) and name:
                    partner = self.env['res.partner'].search([('name', '=', name), ('state_id', '=', state_id)],
                                                             limit=1)
                    if not len(partner):
                        _logger.info(_("Supplier %s with CNPJ %s not found in database") % (name, cnpj_cpf))
                        _logger.info(_("Creating supplier %s") % (name))
                        street = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}xLgr').text
                        number = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}nro').text
                        district = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}xBairro').text
                        zip = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}CEP').text
                        phone = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}fone').text
                        legal_name = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}xFant').text

                        city_code = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}cMun').text
                        city_name = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}xMun').text
                        # search country always will be emited from Brazil
                        country = self.env['res.country'].search([('code', '=ilike', 'BR')], limit=1)
                        if len(country):
                            country_id = country.id

                        # search city:
                        if city_code or city_name:
                            if city_code:
                                city = self.env['l10n_br_base.city'].search([('ibge_code', '=', city_code)], limit=1)
                                if len(city):
                                    city_id = city.id
                            if not city_id and state_id:
                                city = self.env['l10n_br_base.city'].search(
                                    [('name', '=ilike', city_name), ('state_id', '=', state_id)], limit=1)
                                if len(city):
                                    city_id = city.id
                        supplier_dict = {
                            'name': name,
                            'is_company': True,
                            'cnpj_cpf': cnpj_cpf,
                            'type': 'contact',
                            'legal_name': legal_name,
                            'street': street,
                            'number': number,
                            'district': district,
                            'zip': zip,
                            'city': city_name,
                            'l10n_br_city_id': city_id,
                            'state_id': state_id,
                            'country_id': country_id,
                            'phone': phone,
                            'supplier': True,
                            'customer': False,
                        }
                        partner = self.env['res.partner'].create(supplier_dict)
                return partner

            def get_tax(code, amount, domain, company, mva_icmsst):
                domain = domain.lower()
                if domain == 'icmsst':
                    case_code_domain = 'icms'
                else:
                    case_code_domain = domain
                # Use tax name in warning
                if domain.lower() != 'icmsst':
                    tax_name = "%s Entrada %s" % (domain.upper(), str(float(amount) * 100) + '%')
                else:
                    tax_name = "%s Entrada %s MVA %s" % (
                    domain.upper(), str(float(amount) * 100) + '%', str(float(mva_icmsst) * 100) + '%')

                tax_code = self.env['account.tax.code'].search(
                    [('code', '=', code), ('domain', '=ilike', case_code_domain), ('company_id', '=', company.id)],
                    limit=1)
                if domain == 'icmsst':
                    # ICMSST must have different tax base code than ICMS because  ICMS sets Discount this Tax in Prince True in Tax Base code but ICMSST False
                    tax_code = self.env['account.tax.code'].search(
                        [('name', '=ilike', domain), ('code', '=ilike', domain), ('domain', '=ilike', domain),
                         ('company_id', '=', company.id)], limit=1)
                if len(tax_code):
                    tax = self.env['account.tax'].search([('base_code_id', '=', tax_code.id),
                                                          ('type_tax_use', 'in', ['purchase', 'all']),
                                                          ('domain', '=ilike', domain),
                                                          ('company_id', '=', company.id),
                                                          ('amount', '=', amount),
                                                          ('amount_mva', '=', mva_icmsst)],
                                                         limit=1)
                    if len(tax):
                        return {'id': tax.id, 'message': '', 'tax_code': tax_code.id}
                    elif not len(tax) and self.create_taxes:
                        # ============= Auto Create Tax ==================================
                        tax = self.env['account.tax'].create({'base_code_id': tax_code.id,
                                                              'tax_code_id': tax_code.id,
                                                              'ref_base_code_id': tax_code.id,
                                                              'ref_tax_code_id': tax_code.id,
                                                              'type_tax_use': 'purchase',
                                                              'domain': domain.lower(),
                                                              'company_id': company.id,
                                                              'amount': amount,
                                                              'name': tax_name,
                                                              'amount_mva': mva_icmsst,
                                                              'account_collected_id': tax_code.account_collected_id.id,
                                                              'account_paid_id': tax_code.account_paid_id.id,
                                                              'account_deduced_id': tax_code.account_deduced_id.id,
                                                              'account_paid_deduced_id': tax_code.account_paid_deduced_id.id,

                                                              })
                        return {'id': tax.id, 'message': '', 'tax_code': tax_code.id}
                    else:
                        message = _(
                            u"Tax Name: %s  \n Account Base Code: %s \n Company : %s \n Domain : %s, \n Tax percent : %s  \n Tax Application in:  Purchase, All" % (
                            tax_name, code, company.name, domain, amount))
                        return {'id': False, 'message': message}
                else:
                    message = _(
                        u"Tax code not found Tax Case Name: %s \n Company : %s \n Domain : %s, \n Case Code : %s" % (
                        domain, company.name, domain, domain.lower()))
                    return {'id': False, 'message': message, 'tax_code': tax_code.id}
                return {'id': False, 'message': message, 'tax_code': tax_code.id}

            if attachment.index_content:
                try:
                    xml = attachment.index_content.encode('utf-8')
                    root = ET.fromstring(xml)
                    root.findall("./country/neighbor")
                    # search supplier with cnpj_cpf if not found them with name
                    supplier = root.find('.//{http://www.portalfiscal.inf.br/nfe}emit')
                    partner = get_partner(supplier)

                    # NFe Number
                    nfe_number = root.find('.//{http://www.portalfiscal.inf.br/nfe}nNF').text
                    nfe_access_key = root.find('.//{http://www.portalfiscal.inf.br/nfe}chNFe').text

                    if self.invoice_type == 's':
                        type = 'in_invoice'
                        fiscal_category = self.env['l10n_br_account.fiscal.category'].search(
                            [('type', '=', 'input'), ('state', '=', 'approved'), ('journal_type', '=', 'purchase')],
                            limit=1)
                    else:
                        type = 'out_invoice'
                        fiscal_category = self.env['l10n_br_account.fiscal.category'].search(
                            [('type', '=', 'output'), ('state', '=', 'approved'), ('journal_type', '=', 'sale')],
                            limit=1)
                    # create invoice
                    inv_dict = {
                        'partner_id': partner.id,
                        'account_id': partner.property_account_payable.id,
                        'supplier_invoice_number': nfe_number,
                        'nfe_access_key': nfe_access_key,
                        'type': type,
                        'fiscal_type': 'product',
                        'fiscal_category_id': fiscal_category.id,
                        'xml_data': xml,
                    }
                    invoice = self.env['account.invoice'].search([('nfe_access_key', '=', nfe_access_key)], limit=1)
                    invoice_line_ids = []
                    invoice_line_dict = []  # will store dictionaries of invoice line vals
                    po_line_warning = _(
                        "Products with below info not found in purchase order %s:  \n \n" % (po and po.name))
                    po_line_not_found = False
                    # proceed only if invoice not found
                    if not len(invoice):
                        # find all products
                        # uom  : uCom
                        if po:
                            if len(po.order_line) != len(root.findall('.//{http://www.portalfiscal.inf.br/nfe}det')):
                                raise Warning(_("Number of products mismatch in XML: %s, & Purchase order %s: %s" % (
                                len(root.findall('.//{http://www.portalfiscal.inf.br/nfe}det')), po.name,
                                len(po.order_line))))
                            self.env['xml.line.info'].search([('wizard_id', '=', self.id)]).unlink()
                            self.env['poline.info'].search([('wizard_id', '=', self.id)]).unlink()
                        for det in root.findall('.//{http://www.portalfiscal.inf.br/nfe}det'):
                            # match no of products in XML and PO
                            product_name = det.find('.//{http://www.portalfiscal.inf.br/nfe}xProd').text
                            product_code = det.find('.//{http://www.portalfiscal.inf.br/nfe}cProd').text
                            product_uom = det.find('.//{http://www.portalfiscal.inf.br/nfe}uCom').text
                            product_qty = det.find('.//{http://www.portalfiscal.inf.br/nfe}qTrib').text
                            unit_price = det.find('.//{http://www.portalfiscal.inf.br/nfe}vUnTrib').text
                            product_taxes = det.findall('.//{http://www.portalfiscal.inf.br/nfe}imposto/')
                            discount_value = det.find('.//{http://www.portalfiscal.inf.br/nfe}vDesc')
                            product_value = det.find('.//{http://www.portalfiscal.inf.br/nfe}vProd')
                            uom = self.env['product.uom'].search([('name', '=', product_uom)], limit=1)
                            product_cfop = det.find('.//{http://www.portalfiscal.inf.br/nfe}CFOP').text
                            product_ncm = det.find('.//{http://www.portalfiscal.inf.br/nfe}NCM').text
                            cfop = get_cfop(product_cfop)
                            ncm = get_ncm(product_ncm)
                            ncm_id = ncm.get('id')
                            cfop_id = cfop.get('id')

                            if not ncm_id:
                                attachment.write({'state': 'e', 'error_message': ncm.get('error_message')})
                                raise Warning(_(ncm.get('error_message')))
                            if not cfop_id:
                                attachment.write({'state': 'e', 'error_message': cfop.get('error_message')})
                                raise Warning(_(cfop.get('error_message')))

                            discount_percentage = 0.0
                            if product_value != None and discount_value != None:
                                try:
                                    discount_percentage = (float(discount_value.text) * 100) / float(product_value.text)
                                except:
                                    # handle devision by zero
                                    discount_percentage = 0.0
                            if not len(uom):
                                uom_message = _("UoM %s not found in database" % product_uom)
                                attachment.write({'state': 'e', 'error_message': uom_message})
                                raise Warning(uom_message)
                            # search product in product_supplierinfo

                            productinfo = self.env['product.supplierinfo'].search(
                                [('name', '=', partner.id), ('product_code', '=', product_code)], limit=1)
                            if len(productinfo) > 1:
                                raise Warning("Duplicate supplierinfo found for product code %s" % product_code)
                            if len(productinfo):
                                product_template = productinfo.product_tmpl_id
                            else:
                                product_template = self.env['product.template'].search([('name', '=', product_name)],
                                                                                       limit=1)
                                if not len(product_template):
                                    product_template = self.env['product.template'].create({'name': product_name,
                                                                                            'uom_id': uom.id,
                                                                                            'uom_po_id': uom.id,
                                                                                            'type': 'product',
                                                                                            'ncm_id': ncm_id,
                                                                                            'purchase_ok': True,
                                                                                            'default_code': product_code,
                                                                                            })
                                self.env['product.supplierinfo'].create({'name': partner.id,
                                                                         'product_code': product_code,
                                                                         'product_tmpl_id': product_template.id,
                                                                         })
                            # search product based on product template, it will be selected in invoice line
                            product = self.env['product.product'].search(
                                [('product_tmpl_id', '=', product_template.id)], limit=1)
                            if not len(product):
                                raise Warning(_("Product %s not found in database" % product_template.name))
                            # compute taxes of line
                            tax_ids = []
                            message = 'Taxes not found for product %s, \n Please create taxes with below information or select Create Taxes to auto create taxes ..: \n  ' % product.name
                            non_tax_tags = 0
                            icmsst = 0
                            cofins_cst_id = pis_cst_id = icms_cst_id = ipi_cst_id = False
                            for tax_info in product_taxes:
                                tag = tax_info.tag.split('}')[-1]
                                tax_name = tag
                                # some xmls contain tags other than taxes like  vTotTrib
                                if tax_name.lower() not in ['icms', 'ipi', 'icmsst', 'cofins', 'pis']:
                                    non_tax_tags = non_tax_tags + 1
                                    continue
                                # get tax value

                                tax_base = tax_info.find('.//{http://www.portalfiscal.inf.br/nfe}vBC')
                                tax_percent = tax_info.find('.//{http://www.portalfiscal.inf.br/nfe}%s' % ('p' + tag))
                                tax_value = tax_info.find('.//{http://www.portalfiscal.inf.br/nfe}%s' % ('v' + tag))
                                tax_code = tax_info.find('.//{http://www.portalfiscal.inf.br/nfe}CST')

                                if tax_value != None:
                                    tax_amount = float(tax_percent.text) / 100
                                else:
                                    tax_amount = 0.0
                                if tax_code != None:
                                    tax_code = tax_code.text
                                # get_tax(code, amount, domain, company)
                                tax = get_tax(tax_code, tax_amount, tax_name, self.env.user.company_id, 0.0)
                                if tax.get('id'):
                                    tax_ids.append(tax['id'])
                                    if tax_name.lower() == 'cofins':
                                        cofins_cst_id = tax['tax_code']
                                    if tax_name.lower() == 'pis':
                                        pis_cst_id = tax['tax_code']
                                    if tax_name.lower() == 'icms':
                                        icms_cst_id = tax['tax_code']
                                    if tax_name.lower() == 'ipi':
                                        ipi_cst_id = tax['tax_code']
                                else:
                                    message = message + '\n -------------------------- \n' + tax.get('message')
                                # if tax is icms check for icmsst, both are in same tag
                                if tax_name.upper() == 'ICMS':
                                    value_icmsst = tax_info.find('.//{http://www.portalfiscal.inf.br/nfe}vICMSST')
                                    if value_icmsst != None:
                                        icmsst = icmsst + 1
                                        mva_icmsst = tax_info.find('.//{http://www.portalfiscal.inf.br/nfe}pMVAST')
                                        if mva_icmsst == None:
                                            mva_icmsst = 0.0
                                        else:
                                            mva_icmsst = float(mva_icmsst.text) / 100
                                        vICMS = float(
                                            tax_info.find('.//{http://www.portalfiscal.inf.br/nfe}vICMS').text)
                                        vICMSST = float(
                                            tax_info.find('.//{http://www.portalfiscal.inf.br/nfe}vICMSST').text)
                                        vBCST = float(
                                            tax_info.find('.//{http://www.portalfiscal.inf.br/nfe}vBCST').text)
                                        tax_amount = round((vICMS + vICMSST) / vBCST, 3)
                                        icmsst_tax = get_tax(tax_code, tax_amount, 'ICMSST', self.env.user.company_id,
                                                             mva_icmsst)
                                        if icmsst_tax.get('id'):
                                            tax_ids.append(icmsst_tax['id'])
                                        else:
                                            message = message + '\n -------------------------- \n' + icmsst_tax.get(
                                                'message')
                            # if not all taxes found, write message and terminate import
                            # if ICMSST found it is extra tax under ICMS tag
                            if len(product_taxes) + icmsst != len(tax_ids) + non_tax_tags:
                                attachment.write({'state': 'e', 'error_message': message})
                                raise Warning(
                                    ("%s %s %s") % (message, len(product_taxes) + icmsst, len(tax_ids) + non_tax_tags))

                            # create invoice line after taxes comoputation
                            if po:
                                # check if product exists in PO
                                for pol in po.order_line:
                                    # match without unit price"
                                    productinfo = self.env['product.supplierinfo'].search(
                                        [('name', '=', po.partner_id.id), ('product_code', '=', product_code)])
                                    if len(productinfo) > 1:
                                        po_line_warning = po_line_warning + "Name: %s \n Supplier Product Code: %s [Found %s records]\n Quantity: %s\n UoM: %s\n Supplier: %s \n" % (
                                        product_name, product_code, len(productinfo), product_qty, uom.name,
                                        po.partner_id.name)
                                        break
                                    if len(productinfo):
                                        product_template = productinfo.product_tmpl_id
                                    else:
                                        product_template = self.env['product.template'].search(
                                            [('name', '=', product_name)], limit=1)
                                        if not len(product_template):
                                            product_template = self.env['product.template'].create(
                                                {'name': product_name,
                                                 'uom_id': uom.id,
                                                 'uom_po_id': uom.id,
                                                 'type': 'product',
                                                 'ncm_id': ncm_id,
                                                 'purchase_ok': True,
                                                 'default_code': product_code,
                                                 })
                                        self.env['product.supplierinfo'].create({'name': partner.id,
                                                                                 'product_code': product_code,
                                                                                 'product_tmpl_id': product_template.id,
                                                                                 })
                                    product = self.env['product.product'].search(
                                        [('product_tmpl_id', '=', product_template.id)], limit=1)

                                    if po.partner_id.id in [seller.name.id for seller in pol.product_id.seller_ids if
                                                            seller.name] and pol.product_id.id == product.id and float(
                                            pol.product_qty) == float(
                                            product_qty) and pol.product_uom.name.lower() == uom.name.lower():
                                        # match with unit price
                                        if float(pol.price_unit) == float(unit_price) and sorted(tax_ids) == sorted(
                                                [tax.id for tax in pol.taxes_id]):
                                            print "PO line matched..............", sorted(tax_ids)
                                        else:
                                            self.env['poline.info'].create({'product_name': pol.product_id.name,
                                                                            'product_qty': pol.product_qty,
                                                                            'product_uom': pol.product_uom.id,
                                                                            'unit_price': pol.price_unit,
                                                                            'wizard_id': self.id,
                                                                            'tax_ids': [(6, 0, tax_ids)]
                                                                            })
                                            self.env['xml.line.info'].create({'product_name': product_name,
                                                                              'product_qty': product_qty,
                                                                              'product_uom': uom.id,
                                                                              'unit_price': unit_price,
                                                                              'wizard_id': self.id,

                                                                              })
                                            # correct unite price in PO Order
                                            if self.correct_po_from_xml:
                                                pol.write({'price_unit': unit_price, 'taxes_id': [(6, 0, tax_ids)]})
                                        break

                                else:
                                    po_line_warning = po_line_warning + "Name: %s \n Supplier Product Code: %s\n Quantity: %s\n UoM: %s\n Supplier: %s \n" % (
                                    product_name, product_code, product_qty, uom.name, po.partner_id.name)
                                    po_line_not_found = True
                            # append dict with inv line values to create outside of for loop
                            invoice_line_dict.append({'product_id': product.id,
                                                      'name': product_name,
                                                      'quantity': product_qty,
                                                      'price_unit': unit_price,
                                                      'uos_id': uom.id,
                                                      'fiscal_classification_id': ncm_id,
                                                      'invoice_line_tax_id': [(6, False, tax_ids)],
                                                      'discount': discount_percentage,
                                                      'cfop_id': cfop_id,
                                                      'cofins_cst_id': cofins_cst_id,
                                                      'pis_cst_id': pis_cst_id,
                                                      'icms_cst_id': icms_cst_id,
                                                      'ipi_cst_id': ipi_cst_id,
                                                      })
                        if po_line_not_found:
                            raise Warning(_(po_line_warning))
                        if po:
                            if len(self.po_line_info) and not self.correct_po_from_xml:
                                raise Warning(_(
                                    "Products Unit Price or Taxes Mismatch, Click on Show Difference to compare prices"))
                        inv_line_obj = self.env['account.invoice.line']
                        # create invoice lines
                        for invoice_line in invoice_line_dict:
                            inv_line = inv_line_obj.create(invoice_line)
                            invoice_line_ids.append(inv_line.id)
                        # create invoice and set in invoice lines
                        invoice = self.env['account.invoice'].create(inv_dict)
                        self.env['account.invoice.line'].browse(invoice_line_ids).write({'invoice_id': invoice.id})
                        # compute taxes
                        invoice.button_reset_taxes()
                        attachment.write({'state': 'd', 'error_message': 'Imported'})
                        return invoice
                    else:
                        attachment.write(
                            {'state': 'd', 'error_message': 'Invoice already exists with key %s' % nfe_access_key})
                        if po:
                            # return False if wizard was called from PO, considering only one file will be uploaded
                            return False
                except Exception, ex:
                    # set error in attachment
                    attachment.write({'state': 'e', 'error_message': "Error: {0}".format(ex.args[0].encode("utf-8"))})
