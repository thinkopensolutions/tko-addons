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

import logging
import re
from datetime import datetime

from openerp import models, api, fields, _
from openerp.exceptions import Warning
from openerp.osv import osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF

from focusnfe.FocusNF import FocusNF

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    nfse_state = fields.Selection([('e', 'To Issue'),
                                   ('w', 'Processing'),
                                   ('a', 'Approved'),
                                   ('ex', 'Rejected'),
                                   ('c', 'Cancelled')], default="e", copy=False, track_visibility='onchange',
                                  string='NFS-e Status')
    date_hour_invoice = fields.Datetime(
        u'Data e hora de emissão', readonly=True,
        states={'draft': [('readonly', False)]},
        select=True, copy=False, help="Deixe em branco para usar a data atual")

    internal_number = fields.Char('Inetrnal Number', size=60)
    nfse_url = fields.Char("NFSe URL", compute="_get_nfse_url", store=True)

    def _get_foucus_environment(self):
        if not self.company_id.api_environment or not self.company_id.api_token:
            raise Warning(u"Please check Environment and API token for company %s" %self.company_id.name)
        return self.company_id.api_environment, self.company_id.api_token

    @api.depends('internal_number')
    @api.one
    def _get_nfse_url(self):
        self = self.sudo()
        if self.internal_number:
            environment, token = self._get_foucus_environment()
            focus_methods = FocusNF(environment, token)
            nf_dict, http_status_code = focus_methods.get_nfs_by_ref(self.internal_number)
            if 'uri' in nf_dict:
                self.nfse_url = nf_dict['uri']

    @api.one
    def validate_nfse_data(self):
        if not self.company_id:
            raise Warning(_('No Company'))
        if not self.partner_id:
            raise Warning(_('No Partner'))

        company = self.company_id
        partner = self.partner_id
        # check company related fields
        if not company.cnpj_cpf:
            raise Warning(_("Company's  CNPJ not defined for company"))
        if not company.legal_name:
            raise Warning(_("Company's Rezão Social not defined for company"))
        if not company.email:
            raise Warning(_("Company's email not defined for company"))
        if not company.inscr_mun:
            raise Warning(_("Company's  Inscr. Municipal not defined"))
        if not company.country_id:
            raise Warning(_("Company's country not defined"))
        if not company.state_id:
            raise Warning(_("Company's state not defined"))
        if not company.l10n_br_city_id:
            raise Warning(_("Company's city not defined"))
        if not company.zip:
            raise Warning(_("Company's CEP not defined"))
        if not company.api_token:
            raise Warning(_("API Token not set"))

        # check partner related fields
        if not partner.cnpj_cpf:
            raise Warning(_("client's  CNPJ not defined for company"))
        if not partner.legal_name:
            raise Warning(_("client's Rezão Social not defined for company"))
        if not partner.email:
            raise Warning(_("client's email not defined for company"))
        if not partner.country_id:
            raise Warning(_("client's country not defined"))
        if not partner.state_id:
            raise Warning(_("client's state not defined"))
        if not partner.l10n_br_city_id:
            raise Warning(_("client's city not defined"))
        if not partner.zip:
            raise Warning(_("client's CEP not defined"))
        if not self.fiscal_comment:
            raise Warning(_(u"Observações Fiscais not defined"))
        if not self.nfse_description:
            raise Warning(_(u"NFSe description not defined"))
        if not self.move_id:
            raise Warning(u"Please confirm invoice to emit NFse")

    # we do not want to update internal_number on confirm invoice it is reference of request on focus
    @api.multi
    def write(self, vals):
        for record in self:
            if 'internal_number' in vals.keys():
                if record.type == 'out_invoice' and record.fiscal_document_electronic == True and record.nfse_state == 'w':
                    vals.pop('internal_number')
                    vals.pop('number')
        return super(AccountInvoice, self).write(vals)

    @api.one
    def nfse_check(self):
        if self.fiscal_document_electronic and self.type == 'out_invoice':
            self.validate_nfse_data()
        return super(AccountInvoice, self).nfse_check()

    @api.multi
    def view_nfse(self):
        self.ensure_one()
        self = self.sudo()
        environment, token = self._get_foucus_environment()
        focus_methods = FocusNF(environment, token)
        if not self.internal_number:
            raise Warning("No reference found for NFS-e")
        nf_dict, http_status_code = focus_methods.get_nfs_by_ref(self.internal_number)

        if 'uri' in nf_dict:
            nfse_url = nf_dict['uri']
            if not self.nfse_url:
                self.nfse_url = nfse_url
            return {
                'type': 'ir.actions.act_url',
                'name': "NFSe",
                'target': 'new',
                'url': nfse_url,
            }

        else:
            raise Warning("NFSe not found")

    # HTTP status 200 (Ok) ou HTTP status 404 (Not Found)
    @api.multi
    def check_nfse_status(self):
        self = self.sudo()
        self.ensure_one()
        environment, token = self._get_foucus_environment()
        focus_methods = FocusNF(environment, token)
        if not self.internal_number:
            raise Warning("No reference found for NFS-e")
        nf_dict, http_status_code = focus_methods.get_nfs_by_ref(self.internal_number)
        status = nf_dict.get('status')
        context = self._context
        number = nf_dict.get('numero',self.electornic_document_number)
        nfse_url = nf_dict.get('uri', self.nfse_url)
        state = 'ex'
        if http_status_code == 200:
            if status != 'autorizado':
                if context.get('cron'):
                    _logger.info("NFS-e Status for %s : %s" % (self.internal_number, status.replace('_', ' ').title()))
                else:
                    self.write({'nfse_state': state})
                    raise Warning("%s" % status.replace('_', ' ').title())
            else:
                state = 'a'
        # write on invoice
        self.write({'nfse_state': state,
                    'electornic_document_number': number,
                    'nfse_url': nfse_url
                    })

    @api.model
    def nfse_request_status_check(self):
        # all invoices in state waiting for issue nfse
        invoices = self.env['account.invoice'].search([('nfse_state', '=', 'w')])
        ctx = dict(self._context)
        ctx.update({'cron': True})
        for invoice in invoices:
            invoice.with_context(ctx).check_nfse_status()

    # nfse_dict returned when tried cancel with reference
    # {'erros': [{'codigo': 'parametros_invalidos', 'mensagem': u'Campos data_criacao_de e data_criacao_ate sao obrigat\xf3rios'}]}

    @api.multi
    def nfse_cancel(self):
        self = self.sudo()
        self.ensure_one()
        if self.type == 'out_invoice' and self.fiscal_document_electronic == True and self.state in [
            'open'] and self.nfse_state == 'a':
            environment , token = self._get_foucus_environment()
            focus_methods = FocusNF(environment, token)
            nf_dict, http_status_code = focus_methods.cancel_nfse_by_ref(self.internal_number)
            status = nf_dict.get('status')
            if http_status_code == 404:
                raise Warning("NFSe not found with refence : %s" % self.internal_number)
            else:
                self.signal_workflow('invoice_cancel')
            return True
        else:
            # cancel nfse here
            return self.signal_workflow('invoice_cancel')

    def nfse_issue(self):
        for invoice in self:
            invoice.validate_nfse_data()
            re.sub("[\-./]", "", invoice.company_id.cnpj_cpf)
            environment, token = invoice._get_foucus_environment()
            service_code = False
            service_aliquota = False

            # prestador ==  company
            # tomador == partner
            data = {}
            data["prestador"] = {}
            data["tomador"] = {}
            data["servico"] = {}
            data["itens"] = []
            data["tomador"]["endereco"] = {}
            data["data_emissao"] = datetime.strftime(datetime.today().date(), DF)

            for inv_line in invoice.invoice_line:
                if not service_code:
                    if not inv_line.product_id.service_type_id.code:
                        raise Warning(_(u"Service code not defined"))
                    else:
                        service_code = ''.join(
                            digit for digit in inv_line.product_id.service_type_id.code if digit.isdigit())
                        service_aliquota = inv_line.issqn_percent
                data["itens"].append({
                    "discriminacao": inv_line.name,
                    "quantidade": inv_line.quantity,
                    "valor_unitario": inv_line.price_unit,
                    "valor_total": inv_line.price_total,
                    "tributavel": True,
                })

            if invoice.company_id.fiscal_type == 2:
                data["optante_simples_nacional"] = True
            else:
                data["optante_simples_nacional"] = False

            data["servico"][
                "aliquota"] = service_aliquota  # first line, first product, service type --> issqn_percent # Needs to by like that <--

            # 308 - Código do Serviço Prestado (2690) da NFS-e não permite dedução na base de cálculo. ()
            # setting 0.0 because of above error
            data["servico"][
                "valor_deducoes"] = 0.0  # invoice.amount_tax + invoice.amount_tax_withholding  # total value of taxes
            data["servico"]["valor_pis"] = sum(
                [line.amount for line in invoice.withholding_tax_lines if
                 line.base_code_id.domain == 'pis'])  # Value of PIS[pis] tax.
            data["servico"]["valor_cofins"] = sum(
                [line.amount for line in invoice.withholding_tax_lines if
                 line.base_code_id.domain == 'cofins'])  # Value of COFINS[cofins] tax.
            data["servico"]["valor_inss"] = sum(
                [line.amount for line in invoice.withholding_tax_lines if
                 line.base_code_id.domain == 'inss'])  # Value of INSS[inss] tax.
            data["servico"]["valor_ir"] = sum(
                [line.amount for line in invoice.withholding_tax_lines if
                 line.base_code_id.domain == 'irpj'])  # Value of IRPJ[irpj] tax.
            data["servico"]["valor_csll"] = sum(
                [line.amount for line in invoice.withholding_tax_lines if
                 line.base_code_id.domain == 'csll'])  # Value of CSLL[csll] tax.
            data["servico"]["valor_iss"] = sum([line.amount for line in invoice.withholding_tax_lines if
                                                line.base_code_id.domain == 'issqn'])  # Value of ISSQN[issqn] tax.
            data["servico"]["valor_iss_retido"] = sum([line.tax_amount for line in invoice.withholding_tax_lines if
                                                       line.base_code_id.domain == 'issqn'])  # Value of withheld ISSQN[issqn] tax.
            data["servico"]["outras_retencoes"] = sum([line.tax_amount for line in invoice.withholding_tax_lines if
                                                       line.base_code_id.domain != 'issqn'])  # Value of other withheld taxes.
            data["servico"]["base_calculo"] = sum([line.base for line in invoice.tax_line if
                                                   line.base_code_id.domain == 'issqn'])  # Value of base for ISSQN[issqn] tax.
            data["servico"]["desconto_incondicionado"] = 0.0  # Value of unconditioned discount. ????
        data["servico"]["desconto_condicionado"] = 0.0  # Value of conditioned discount. ????
        data["servico"]["codigo_cnae"] = invoice.company_id.cnae_main_id.code  # Company's CNAE code.
        data["servico"]["codigo_municipio"] = str(invoice.company_id.state_id.ibge_code) + str(
            invoice.company_id.l10n_br_city_id.ibge_code)  # Company's address city ibge code. # Needs new field in invoice.
        data["servico"]["discriminacao"] = invoice.nfse_description  # Service description.
        data["servico"]["valor_servicos"] = invoice.amount_untaxed  # Untaxed total value of services.
        data["servico"][
            "iss_retido"] = False  # True or False for withheld ISSQN[issqn]. # Needs to be like that <--
        data["servico"]["item_lista_servico"] = str(service_code)  # Service code.
        if invoice.partner_id.is_company:
            data["tomador"]["cnpj"] = re.sub("[\-./]", "", invoice.partner_id.cnpj_cpf)  # Partner's CNPJ.
        else:
            data["tomador"]["cpf"] = re.sub("[\-./]", "", invoice.partner_id.cnpj_cpf)  # Partner's CPF.
        data["tomador"]["razao_social"] = invoice.partner_id.legal_name  # Partner's legal name.
        data["tomador"]["email"] = invoice.partner_id.email  # Partner's email.
        data["tomador"]["telefone"] = invoice.partner_id.phone and re.sub("[\-./]", "",
                                                                          invoice.partner_id.phone) or ''  # Partner's phone number.

        data["tomador"]["inscricao_municipal"] = invoice.partner_id.inscr_mun  # Partner's cityhall number.
        data["tomador"]["endereco"]["tipo_logradouro"] = "-"  # Partner's address type.
        data["tomador"]["endereco"]["codigo_municipio"] = str(invoice.partner_id.state_id.ibge_code) + str(
            invoice.partner_id.l10n_br_city_id.ibge_code)  # Partner's address city ibge code.
        data["tomador"]["endereco"]["uf"] = invoice.partner_id.state_id.code  # Partner's address state ibge code.
        data["tomador"]["endereco"]["logradouro"] = invoice.partner_id.street  # Partner's address street.
        data["tomador"]["endereco"]["cep"] = invoice.partner_id.zip  # Partner's address zip.
        data["tomador"]["endereco"]["numero"] = invoice.partner_id.number  # Partner's address number.
        data["tomador"]["endereco"]["complemento"] = invoice.partner_id.street2  # Partner's address complement.
        data["tomador"]["endereco"]["bairro"] = invoice.partner_id.district  # Partner's address neighbour.
        data["prestador"]["cnpj"] = re.sub("[\-./]", "", invoice.company_id.cnpj_cpf)  # Company's CNPJ.
        data["prestador"]["inscricao_municipal"] = re.sub("[\-./]", "",
                                                          invoice.company_id.inscr_mun)  # Company's cityhall number.
        data["prestador"][
            "codigo_municipio"] = str(
            invoice.company_id.state_id.ibge_code) + invoice.company_id.l10n_br_city_id.ibge_code  # Company's address city ibge code.
        # this method sends nfe and sets state to one of nfse_exception, nfse_denied
        invoice = self.pool.get('account.invoice').browse(cr, uid, ids, context=context)
        date_hour_invoice = datetime.now()
        ref = invoice.move_id.name

        focus_methods = FocusNF(environment, token)
        nf_data, http_status_code, reason, err_msg = focus_methods.send_request_to_nfs(ref, data)
        # store link in invoice
        self._get_nfse_url()
        msg_type = "Warning!"
        if http_status_code == 202:
            msg_type = "Success!"
            msg = "NFS-e Emitida com sucesso."
            self.write({'nfse_state': 'w', 'date_hour_invoice': date_hour_invoice, 'internal_number': ref})
            _logger.info(msg)
            return True
        elif http_status_code == 400:
            raise Warning(u'Erro ao emitir NFS-e. %s \n\r Ref: %s' % (err_msg, ref))
        else:
            msg = str(" emitir. \n\r Ref: " + ref + " \n\r Status_code: " + str(http_status_code))
        self.write({'nfse_state': 'ex'})
        raise osv.except_osv(_(msg_type + " \n\r err:" + err_msg), _(msg))


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    issqn_percent = fields.Float('ISSQN Percent')

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='',
                          type='out_invoice', partner_id=False,
                          fposition_id=False, price_unit=False,
                          currency_id=False, company_id=None):
        result = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty, name, type, partner_id,
            fposition_id, price_unit, currency_id, company_id)
        if product:
            issqn_percent = self.env['product.product'].browse(product).service_type_id.issqn_percent
            result['value'].update({'issqn_percent': issqn_percent})
        else:
            result['value'].update({'issqn_percent': 0.0})
        return result
