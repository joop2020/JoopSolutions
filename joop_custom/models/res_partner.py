# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    manufacturer_id = fields.Many2one(
        comodel_name='res.partner',
        string='Fabricante',
    )