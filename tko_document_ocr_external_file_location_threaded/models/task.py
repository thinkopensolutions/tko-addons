# coding: utf-8
# @ 2015 Valentin CHEMIERE @ Akretion
#  © @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os
import threading

import odoo
from odoo import models, api
# from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.tko_document_ocr.models.ir_attachment import \
    _PDF_OCR_DOCUMENTS_THREADS

_logger = logging.getLogger(__name__)


class Task(models.Model):
    _inherit = 'external.file.task'

    def _import_file_threaded(self, attach_obj, conn, file_name):
        md5_datas = ''
        with api.Environment.manage():
            with odoo.registry(
                    self.env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(new_cr, self.env.uid,
                                          self.env.context)
                try:
                    full_path = os.path.join(self.filepath, file_name)
                    file_data = conn.open(full_path, 'rb')
                    datas = file_data.read()
                    if self.md5_check:
                        md5_file = conn.open(full_path + '.md5', 'rb')
                        md5_datas = md5_file.read().rstrip('\r\n')
                    attach_vals = self._prepare_attachment_vals(
                        datas, file_name, md5_datas)
                    attachment = attach_obj.with_env(new_env).create(
                        attach_vals)
                    new_full_path = False
                    if self.after_import == 'rename':
                        new_name = self._template_render(
                            self.new_name, attachment)
                        new_full_path = os.path.join(
                            self.filepath, new_name)
                    elif self.after_import == 'move':
                        new_full_path = os.path.join(
                            self.move_path, file_name)
                    elif self.after_import == 'move_rename':
                        new_name = self._template_render(
                            self.new_name, attachment)
                        new_full_path = os.path.join(
                            self.move_path, new_name)
                    if new_full_path:
                        conn.rename(full_path, new_full_path)
                        if self.md5_check:
                            conn.rename(
                                full_path + '.md5',
                                new_full_path + '/md5')
                    if self.after_import == 'delete':
                        conn.remove(full_path)
                        if self.md5_check:
                            conn.remove(full_path + '.md5')
                except Exception, e:
                    new_env.cr.rollback()
                    _logger.error('Error importing file %s '
                                  'from %s: %s',
                                  file_name,
                                  self.filepath,
                                  e)
                    # move on to process other files
                else:
                    new_env.cr.commit()

    @api.multi
    def run_import(self):
        self.ensure_one()
        protocols = self.env['external.file.location']._get_classes()
        cls = protocols.get(self.location_id.protocol)[1]
        attach_obj = self.env['ir.attachment.metadata']
        try:
            connection = cls.connect(self.location_id)
            with connection as conn:
                try:
                    files = conn.listdir(path=self.filepath,
                                         wildcard=self.filename or '',
                                         files_only=True)
                    for file_name in files:
                        t = threading.Thread(target=self._import_file_threaded,
                                             name=u'import_file' + file_name,
                                             args=(attach_obj,
                                                   conn,
                                                   file_name))
                        t.start()
                    for t in _PDF_OCR_DOCUMENTS_THREADS:
                        t.join()
                except:
                    _logger.error('Directory %s does not exist', self.filepath)
                    return
        except:
            _logger.error('Root directory %s does not exist', self.filepath)
            return