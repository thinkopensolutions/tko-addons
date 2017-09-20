# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
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
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import base64

def generate_record(self,vals):
    xml = vals.encode('utf-8')
    root = ET.fromstring(xml)
    root.findall("./country/neighbor")
    supplier = root.find('.//{http://www.portalfiscal.inf.br/nfe}emit')
    invoice_num = root.find('.//{http://www.portalfiscal.inf.br/nfe}nNF').text
    i_date = root.find('.//{http://www.portalfiscal.inf.br/nfe}ide')
    invoice_date = i_date.find(".//{http://www.portalfiscal.inf.br/nfe}dhEmi").text
    i_due_date = root.find('.//{http://www.portalfiscal.inf.br/nfe}cobr')
    due_date = i_due_date.find(".//{http://www.portalfiscal.inf.br/nfe}dup")
    invoice_due_date = due_date.find(".//{http://www.portalfiscal.inf.br/nfe}dVenc").text
    supplier_name = supplier.find('.//{http://www.portalfiscal.inf.br/nfe}xNome').text
    inv_dict = {
        'supplier': supplier_name,
        'invoice_date':invoice_date,
        'invoice_due_date': invoice_due_date,
        'invoice_num':invoice_num

    }

    invoice = self.env['account.invoice.xml.form'].create(inv_dict)
    total = 0.0
    for product in root.findall('.//{http://www.portalfiscal.inf.br/nfe}prod'):
        product_name = product.find('.//{http://www.portalfiscal.inf.br/nfe}xProd').text
        product_uom = product.find('.//{http://www.portalfiscal.inf.br/nfe}uCom').text
        product_qty = product.find('.//{http://www.portalfiscal.inf.br/nfe}qCom').text
        unit_price = product.find('.//{http://www.portalfiscal.inf.br/nfe}vUnCom').text
        total +=  float(product_qty) * float(unit_price)
        self.env['account.invoice.line.xml'].create(
                    {'invoice_line_xml_id': invoice.id,
                    'product': product_name,
                    'qty': product_qty,
                    'uom':product_uom,
                    'total': float(product_qty) * float(unit_price), 
                    'unit_price': unit_price,
                    })
    invoice.total = total  

class AccountInvoiceXmlFormWizard(models.TransientModel):
    _name = "account.invoice.xml.wizard"
    _description = "Invoice Xml Wizard"
    _inherit = ['mail.thread']

    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name':  msg.get('subject') or _("No Subject"),
            }
        defaults.update(custom_values)
        return super(AccountInvoiceXmlFormWizard, self).message_new(cr, uid, msg, custom_values=defaults, context=context)


    file = fields.Binary(string="File")
    xml_data = fields.Text(string='XML', copy=False)
    name= fields.Char('Name')
    
    @api.onchange('file')
    def onchange_file(self):
        if self.file:
            data = base64.decodestring(self.file)
            self.xml_data= data

    @api.multi
    def import_file(self):
        if self.xml_data:
            generate_record(self,self.xml_data)

class ir_attachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def create(self, vals):
        model = vals.get('res_model', False)
        if model == 'account.invoice.xml.wizard':
            type = vals.get('datas_fname').endswith('.xml')
            if type:
                data = base64.decodestring(vals.get('datas',False))
                generate_record(self, data)
        res = super(ir_attachment, self).create(vals)
        return res
