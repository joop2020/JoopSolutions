from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    project_type_id = fields.Many2one(
        'project.type',
        string='Tipo de Proyecto',
        help='Tipo de proyecto que se creará desde esta oportunidad'
    )
    project_ids = fields.One2many(
        'project.project',
        'crm_lead_id',
        string='Proyectos'
    )
    project_count = fields.Integer(
        string='Cantidad de Proyectos',
        compute='_compute_project_count',
        store=True
    )

    @api.depends('project_ids')
    def _compute_project_count(self):
        for lead in self:
            lead.project_count = len(lead.project_ids)

    def action_create_project(self):
        """Crea un proyecto desde la plantilla asociada al tipo de proyecto"""
        self.ensure_one()

        if not self.project_type_id:
            raise UserError(_('Debe seleccionar un tipo de proyecto primero.'))

        if not self.project_type_id.project_template_id:
            raise UserError(_(
                'El tipo de proyecto "%s" no tiene una plantilla configurada.',
                self.project_type_id.name
            ))

        template = self.project_type_id.project_template_id

        values = {
            'name': self.name,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'crm_lead_id': self.id,
            'project_type_id': self.project_type_id.id,
            'user_id': self.user_id.id if self.user_id else self.env.uid,
        }

        project = template.action_create_from_template(values=values)

        self.message_post(
            body=_('Proyecto "%s" creado desde plantilla "%s".', project.name, template.name)
        )

        return {
            'type': 'ir.actions.act_window',
            'name': _('Proyecto'),
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_projects(self):
        """Abre la lista de proyectos vinculados a esta oportunidad"""
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('project.open_view_project_all')
        action['domain'] = [('crm_lead_id', '=', self.id)]
        action['context'] = {
            'default_crm_lead_id': self.id,
            'default_partner_id': self.partner_id.id if self.partner_id else False,
            'default_project_type_id': self.project_type_id.id if self.project_type_id else False,
        }
        if self.project_count == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.project_ids.id
        return action