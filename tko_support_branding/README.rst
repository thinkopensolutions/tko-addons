.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Support branding
================

If you run an Odoo support company and you support customers without an OPW,
you can brand the Odoo instance accordingly using this module. This module will
add a line `Supported by $yourcompany` in the menu footer and add a button to
mail exception messages to your support email address.


Configuration
=============

This module is controlled by config parameters:

support_branding.company_name
    Your company's name

support_branding.company_url
    Your company's website

support_branding.company_color
    The color to show your company's name in (CSS syntax)

support_branding.support_email
    The (optional) mailaddress to contact for support

support_branding.release
    The (optional) version number of your deployment

You probably want to depend on this module in your customer specific module and
add the following XML::

  <record id="support_branding.config_parameter_company_name" model="ir.config_parameter">
      <field name="value">Your company</field>
  </record>
  <record id="support_branding.config_parameter_company_url" model="ir.config_parameter">
      <field name="value">https://yourwebsite.com</field>
  </record>
  <record id="support_branding.config_parameter_company_color" model="ir.config_parameter">
      <field name="value">#000</field>
  </record>
  <record id="support_branding.config_parameter_support_email" model="ir.config_parameter">
      <field name="value">support@yourwebsite.com</field>
  </record>
  <record id="config_parameter_release" model="ir.config_parameter">
      <field name="value">42</field>
  </record>Configuration

Note that the email button is only visible if you configure an email address,
the default is empty!