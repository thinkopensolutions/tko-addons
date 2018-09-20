# -*- coding: utf-8 -*-
{
    "name": "Resend Failed Emails",
    "summary": """Quick way to find failed sent messages and resend them""",
    "category": "Discuss",
    "images": ['images/menu.png'],
    "version": "1.0.4",

    "author": "IT-Projects LLC, Ivan Yelizariev, Pavel Romanchenko, Yogesh Kushwaha",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "LGPL-3",

    "depends": [
        "mail",
        "mail_sent",
    ],

    "data": [
        "views/templates.xml",
    ],
    "qweb": [
        "static/src/xml/menu.xml",
    ],
    'installable': True,
}
