# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os

from openerp import api, fields, models, _
from openerp.exceptions import Warning
from openerp.tools import human_size

_logger = logging.getLogger(__name__)


class IrFilesystemDirectoryLine(models.TransientModel):
    _name = 'ir.filesystem.file'

    name = fields.Char(required=True)
    filename = fields.Char()
    file_content = fields.Binary(compute='_compute_file')
    stored_filename = fields.Char()
    directory_id = fields.Many2one(
        'ir.filesystem.directory',
        string='Directory'
    )

    @api.multi
    def _file_read(self, fname, bin_size=False):

        def file_not_found(fname):
            raise Warning(_(
                '''Error while reading file %s.
                Maybe it was removed or permission is changed.
                Please refresh the list.''' % fname))

        self.ensure_one()
        r = ''
        dir = self.directory_id.get_dir() or ''
        full_path = dir + fname
        if not (dir and os.path.isfile(full_path)):
            file_not_found(fname)
        try:
            if bin_size:
                r = human_size(os.path.getsize(full_path))
            else:
                r = open(full_path, 'rb').read().encode('base64')
        except (IOError, OSError):
            _logger.info("_read_file reading %s", fname, exc_info=True)
        return r

    @api.depends('stored_filename')
    def _compute_file(self):
        bin_size = self._context.get('bin_size')
        for line in self:
            if line.stored_filename:
                content = line._file_read(line.stored_filename, bin_size)
                line.file_content = content
