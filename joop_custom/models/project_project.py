from odoo import api, fields, models, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_type_id = fields.Many2one(
        'project.type',
        string='Tipo de Proyecto',
        help='Clasificación del tipo de proyecto'
    )
    crm_lead_id = fields.Many2one(
        'crm.lead',
        string='Oportunidad',
        help='Oportunidad de CRM desde la que se creó este proyecto'
    )
    crm_lead_count = fields.Integer(
        string='Oportunidades',
        compute='_compute_crm_lead_count'
    )

    @api.depends('crm_lead_id')
    def _compute_crm_lead_count(self):
        for project in self:
            project.crm_lead_count = 1 if project.crm_lead_id else 0

    def action_view_crm_lead(self):
        """Abre la oportunidad de origen"""
        self.ensure_one()
        if not self.crm_lead_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Oportunidad'),
            'res_model': 'crm.lead',
            'res_id': self.crm_lead_id.id,
            'view_mode': 'form',
            'target': 'current',
        }