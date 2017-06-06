OCR for documents
=================

This module was written to make uploaded documents, for example scans, searchable by running OCR on them.

It supports all image formats Pillow supports for reading and PDFs.

Installation
============

To install this module, you need to:
------------------------------------

- install tesseract and the language(s) your documents use
- if you want to support OCR on PDFs, install imagemagick
- install the module itself

On an Debian or Ubuntu system you would typically run:

``$ sudo apt-get install tesseract-ocr imagemagick``

Configuration
=============

To configure this module, go to:
--------------------------------

- Settings/Technical/Parameters/System parameters and review the parameters with names document_ocr.*

Usage
=====

By default, character recognition is done asynchronously by a cronjob at night. This is because the recognition process takes a while and you don't want to make your users wait for the indexation to finish. The interval to run the cronjob can be adjusted to your needs in the Scheduled Actions menu, under ` Settings`. In case you want to force the OCR to be done immediately, set configuration parameter document_ocr.synchronous to value True.

By default, recognition language is set to english. In case you want to use a different default, set configuration parameter document_ocr.language to value respective value ex:por, for Portuguese.

In PDF case, OCR will run after it will be converted to an image. But OCR will be applied to all PDFs.

System parameters used:
- document_ocr.synchronous: bool
- document_ocr.language: string
- document_ocr.dpi: integer
- document_ocr.quality: integer

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>
* Carlos Almeida <carlos.almeida@tkobr.com>

Maintainer
----------

![alt tag](http://tkobr.tkobr.com/logo.png)

This module is maintained by TKO (ThinkOpen Solutions Brasil).

To contribute to this module, please visit https://github.com/thinkopensolutions/tkobr-addons/issues.
