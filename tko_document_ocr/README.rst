.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=================
OCR for documents
=================

This module was written to make uploaded documents, for example scans, searchable by running OCR on them.

It supports all image formats `Pillow supports <http://pillow.readthedocs.io/en/3.2.x/handbook/image-file-formats.html>`_ for reading and PDFs.

Installation
============

To install this module, you need to:

#. install tesseract and the language(s) your documents use
#. if you want to support OCR on PDFs, install imagemagick
#. install the module itself

On an Debian or Ubuntu system you would typically run::

    $ sudo apt-get install tesseract-ocr imagemagick


Configuration
=============

To configure this module, go to:

#. Settings/Technical/Parameters/System parameters and review the parameters with names document_ocr.*

Usage
=====

By default, character recognition is done asynchronously by a cronjob at night. 
This is because the recognition process takes a while and you don't want to make your users wait for the indexation to finish.
The interval to run the cronjob can be adjusted to your needs in the ``Scheduled Actions`` menu, under ` `Settings``.
In case you want to force the OCR to be done immediately, set configuration parameter ``document_ocr.synchronous`` to value ``True``.


By default, recognition language is set to english.
In case you want to use a different default, set configuration parameter ``document_ocr.language`` to value respective value ex:``por``, for Portuguese.


In PDF case, OCR will run after it will be converted to an image. But OCR will be applied to all PDFs.


System parameters used:

* ``document_ocr.synchronous``:  bool
* ``document_ocr.language``:  string
* ``document_ocr.dpi``:  integer
* ``document_ocr.quality``:  integer


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/thinkopensolutions/tko-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

The actual work
---------------

* `tesseract <https://github.com/tesseract-ocr>`_

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>  
* Carlos Almeida <carlos.almeida@tkobr.com>


Maintainer
----------

This module is maintained by ThinkOpen Solutions Brasil.


To contribute to this module, please visit https://github.com/thinkopensolutions/tko-addons/issues.
