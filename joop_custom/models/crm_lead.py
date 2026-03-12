from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    project_type_id = fields.Many2one(
        'project.type',
        string='Tipo de Proyecto',
        help='Tipo de proyecto que se creará desde esta oportunidad'
    )