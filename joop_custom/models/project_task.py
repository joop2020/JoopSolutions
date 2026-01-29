from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    purchase_order_ids = fields.Many2many(
        'purchase.order',
        string='Órdenes de Compra',
        copy=False,
        help='Órdenes de compra vinculadas a esta tarea'
    )
    purchase_order_count = fields.Integer(
        string='Cantidad OC',
        compute='_compute_purchase_order_count'
    )

    @api.depends('purchase_order_ids')
    def _compute_purchase_order_count(self):
        for task in self:
            task.purchase_order_count = len(task.purchase_order_ids)

    def action_view_purchase_orders(self):
        """Abre las órdenes de compra vinculadas"""
        self.ensure_one()
        if not self.purchase_order_ids:
            return False

        action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_form_action')
        if len(self.purchase_order_ids) == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.purchase_order_ids.id
        else:
            action['domain'] = [('id', 'in', self.purchase_order_ids.ids)]
        return action

    def action_create_purchase_order(self):
        """Abre formulario para crear nueva orden de compra"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nueva Orden de Compra',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_task_id': self.id,
                'default_project_id': self.project_id.id if self.project_id else False,
                'default_origin': f'[Tarea] {self.name}',
            },
        }