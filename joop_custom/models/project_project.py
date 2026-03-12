from odoo import api, fields, models, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_type_id = fields.Many2one(
        'project.type',
        string='Tipo de Proyecto',
        help='Clasificación del tipo de proyecto'
    )
