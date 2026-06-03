from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    syscom_client_id = fields.Char(
        string="Syscom Client ID",
        config_parameter="joop_syscom_api.client_id",
    )
    syscom_client_secret = fields.Char(
        string="Syscom Client Secret",
        config_parameter="joop_syscom_api.client_secret",
    )

    def action_syscom_test_connection(self):
        """Prueba la conexión con las credenciales guardadas."""
        self.ensure_one()
        self.env["joop.syscom.api"].test_connection()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "title": "SYSCOM",
                "message": "Conexión exitosa con el API de SYSCOM.",
                "sticky": False,
            },
        }