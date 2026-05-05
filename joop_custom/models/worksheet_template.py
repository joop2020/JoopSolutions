from odoo import api, models


class WorksheetTemplate(models.Model):
    _inherit = 'worksheet.template'

    @api.model
    def _create_joop_fsm_fields(self):
        template = self.env.ref('joop_custom.joop_fsm_worksheet_template', raise_if_not_found=False)
        if not template or not template.model_id:
            return
        model_id = template.model_id.id

        existing_names = set(self.env['ir.model.fields'].search([
            ('model_id', '=', model_id),
        ]).mapped('name'))

        bool_other_sections = [
            ('limpieza', 'Site limpio'),
            ('reinicio', 'Se reinició'),
            ('estado', 'Equipos en buen estado'),
            ('mikrotik', 'Mikrotik sin problemas'),
            ('vpn', "VPN's sin problemas"),
            ('extreme', 'Equipos sin problema'),
            ('ssid', 'Wifi con conectividad'),
            ('impresion', 'Equipos de impresión en buen estado'),
            ('office365', 'Office 365 correcto'),
            ('cobertura', 'Señal óptima en redes wifi'),
        ]

        vals = []
        for key, label in bool_other_sections:
            vals.append({
                'name': f'x_{key}_ok',
                'ttype': 'boolean',
                'field_description': label,
                'model_id': model_id,
            })
            vals.append({
                'name': f'x_{key}_other',
                'ttype': 'text',
                'field_description': f'Other ({key})',
                'model_id': model_id,
            })

        vals += [
            {
                'name': 'x_velocidad',
                'ttype': 'char',
                'field_description': 'Velocidad enlace proveedor de internet',
                'required': True,
                'model_id': model_id,
            },
            {
                'name': 'x_actualizacion_ids',
                'ttype': 'many2many',
                'relation': 'joop.equipment.type',
                'field_description': 'Equipos actualizados',
                'model_id': model_id,
            },
            {
                'name': 'x_actualizacion_other',
                'ttype': 'text',
                'field_description': 'Other (actualización)',
                'model_id': model_id,
            },
            {
                'name': 'x_usuario_inconveniente',
                'ttype': 'text',
                'field_description': 'Usuario con inconveniente',
                'required': True,
                'model_id': model_id,
            },
            {
                'name': 'x_fecha',
                'ttype': 'date',
                'field_description': 'Fecha de visita',
                'model_id': model_id,
            },
            {
                'name': 'x_firma',
                'ttype': 'binary',
                'field_description': 'Firma del técnico',
                'model_id': model_id,
            },
        ]

        vals = [v for v in vals if v['name'] not in existing_names]
        if vals:
            self.env['ir.model.fields'].create(vals)

    @api.model
    def _create_joop_fsm_automation(self):
        template = self.env.ref('joop_custom.joop_fsm_worksheet_template')
        model = template.model_id
        if not model:
            return

        existing = self.env['base.automation'].search([
            ('model_id', '=', model.id),
            ('name', '=', 'Joop FSM: validación de hoja técnica'),
        ], limit=1)
        if existing:
            return

        code = (
            "sections = [\n"
            "    ('limpieza', 'Limpieza gabinete'),\n"
            "    ('reinicio', 'Reinicio impresora'),\n"
            "    ('estado', 'Estado físico de los equipos'),\n"
            "    ('mikrotik', 'Revisión Mikrotik'),\n"
            "    ('vpn', \"Revisión VPN's (Mikrotik)\"),\n"
            "    ('extreme', 'Revisión portal Extreme Cloud IQ'),\n"
            "    ('ssid', 'Conectividad en todos los SSID'),\n"
            "    ('impresion', 'Revisión de equipo de impresión'),\n"
            "    ('office365', 'Revisión portal Office 365'),\n"
            "    ('cobertura', 'Recorrido cobertura wifi'),\n"
            "]\n"
            "for rec in records:\n"
            "    missing = []\n"
            "    for key, label in sections:\n"
            "        ok = rec['x_' + key + '_ok']\n"
            "        other = (rec['x_' + key + '_other'] or '').strip()\n"
            "        if not ok and not other:\n"
            "            missing.append(label)\n"
            "    if not rec.x_actualizacion_ids and not (rec.x_actualizacion_other or '').strip():\n"
            "        missing.append('Revisión actualización de equipos')\n"
            "    if missing:\n"
            "        raise UserError(\n"
            "            'Debe marcar la casilla OK o llenar el campo \"Other\" en las siguientes secciones:\\n- '\n"
            "            + '\\n- '.join(missing)\n"
            "        )\n"
        )

        action = self.env['ir.actions.server'].create({
            'name': 'Joop FSM: validar hoja técnica',
            'model_id': model.id,
            'state': 'code',
            'code': code,
        })

        self.env['base.automation'].create({
            'name': 'Joop FSM: validación de hoja técnica',
            'model_id': model.id,
            'trigger': 'on_create_or_write',
            'action_server_ids': [(6, 0, [action.id])],
        })
