from odoo import api, fields, models, tools, _

class MyModuleMessageWizard(models.TransientModel):
    _name = 'erpify.notifications.message.wizard'
    _description = "Show Message"

    message = fields.Text('Message', required=True)

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}

    def show_success(self, message = None, title = 'Success'):
        message_id = self.create({'message': message})
        return {
            'name': title,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'erpify.notifications.message.wizard',
            'res_id': message_id.id,
            'target': 'new'
        }
