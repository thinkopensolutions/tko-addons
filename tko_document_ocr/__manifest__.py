# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "OCR for Documents",
    "version": "10.0.1.0.0",
    "author": "Therp BV,"
              " Odoo Community Association (OCA),"
              " ThinkOpen Solutions Brasil",
    "license": "AGPL-3",
    "category": "Knowledge Management",
    "summary": """OCR for documents

This module was written to make uploaded documents, for example scans, searchable by running OCR on them.

It supports all image formats Pillow supports for reading and PDFs.

Installation

To install this module, you need to:
 1. install tesseract and the language(s) your documents use
 2. if you want to support OCR on PDFs, install imagemagick
 3. install the module itself

On an Debian or Ubuntu system you would typically run:
$ sudo apt-get install tesseract-ocr imagemagick

Configuration

To configure this module, go to:
 1. Settings/Technical/Parameters/System parameters and review the parameters with names document_ocr.*

Usage

By default, character recognition is done asynchronously by a cronjob at night. This is because the recognition process takes a while and you don't want to make your users wait for the indexation to finish. The interval to run the cronjob can be adjusted to your needs in the Scheduled Actions menu, under ` Settings`. In case you want to force the OCR to be done immediately, set configuration parameter document_ocr.synchronous to value True.

By default, recognition language is set to english. In case you want to use a different default, set configuration parameter document_ocr.language to value respective value ex:por, for Portuguese.

In PDF case, OCR will run after it will be converted to an image. But OCR will be applied to all PDFs.

System parameters used:
 - document_ocr.synchronous: bool
 - document_ocr.language: string
 - document_ocr.dpi: integer
 - document_ocr.quality: integer

Contributors

 - Holger Brunn <hbrunn@therp.nl>
 - Carlos Almeida <carlos.almeida@tkobr.com>

Maintainer

This module is maintained by ThinkOpen Solutions Brasil.

To contribute to this module, please visit https://github.com/thinkopensolutions/tko-addons/issues.
               """,
    "depends": [
        'document',
    ],
    "data": [
        "data/ir_cron.xml",
        "data/ir_config_parameter.xml",
        "views/ir_attachment_view.xml",
    ],
    "external_dependencies": {
        'bin': [
            'tesseract',
            'convert',
        ],
    },
}
