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

from odoo import models, fields

_logger = logging.getLogger(__name__)


class WebHooks(models.Model):
    _name = 'github.webhook'
    _description = 'Github Webhook'
    _sort = 'create_date desc'

    name = fields.Char('Name', required=True)
    event = fields.Selection([('coc', 'Commit or diff commented on'),
                              ('brctc', 'Branch or tag created'),
                              ('brctd', 'Branch or tag deleted.'),
                              ('dpl', 'Repository deployed'),
                              ('bpls',
                               'Deployment status updated from the API'),
                              ('fork', 'Repository forked'),
                              ('wiki', 'Wiki page updated'),
                              ('issuec',
                               'Issue comment created, edited, or deleted'),
                              ('issue',
                               'Issue opened, edited, closed, reopened, assigned, unassigned, labeled, unlabeled, milestoned, or demilestoned'),
                              ('lbl', 'Label created, edited or deleted'),
                              ('col',
                               'Collaborator added to, removed from, or has changed permissions for a repository'),
                              ('mem', 'Team membership added or removed. '),
                              ('mil',
                               'Milestone created, closed, opened, edited, or deleted'),
                              ('oblck',
                               'A user has been blocked or unblocked'),
                              ('org',
                               'User invited to, added to, or removed from an organization'),
                              ('pgb', 'Pages site built'),
                              ('prj', 'Project created, updated, or deleted'),
                              ('prjcard',
                               'Project card created, updated, or deleted'),
                              ('prjcol',
                               ' Project column created, updated, moved or deleted'),
                              ('visi',
                               'Repository changes from private to public'),
                              ('pr',
                               'Pull request opened, closed, reopened, edited, assigned, unassigned, review requested, review request removed, labeled, unlabeled, or synchronized'),
                              ('prr',
                               'Pull request review submitted, edited, or dismissed'),
                              ('prrc',
                               'Pull request diff comment created, edited, or deleted'),
                              ('push', 'Git push to a repository'),
                              ('rel', 'Release published in a repository'),
                              ('rep',
                               'Repository created, deleted, archived, unarchived, publicized, or privatized'),
                              ('stat', 'Commit status updated from the API'),
                              ('team',
                               'Team is created, deleted, edited, or added to/removed from a repository'),
                              ('teama',
                               'Team added or modified on a repository'),
                              ('watch', 'User stars a repository'), ],
                             'Event')
    payload = fields.Text('Payload', required=True)
