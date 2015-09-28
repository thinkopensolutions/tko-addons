# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

{
    'name': 'Capture partner picture with webcam',
    'version': '1.002',
    'category': 'Generic Modules',
    'description': """
WebCam
=========

Capture partner pictures with an attached web cam.
    """,
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>,"
    "Odoo Community Association (OCA)"
    "ThinkOpen Solutions Brasil",
    'website': 'http://tkobr.com',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'js': [
        'static/src/js/jquery.webcam.js',
        'static/src/js/webcam.js',
    ],
    'css': [
        'static/src/css/webcam.css',
    ],
    'qweb': [
        'static/src/xml/webcam.xml',
    ],
    'data': [
        'webcam_data.xml',
        'webcam_view.xml',
    ],
    'installable': True,
    'active': False,
}
