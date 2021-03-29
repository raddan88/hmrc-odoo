from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class Contract(models.Model):
    _inherit = 'hr.contract'
    hmrc_tax_code = fields.Char('HMRC Tax Code')

    hmrc_schedule_pay = fields.Selection([
        ('W1', 'Weekly'),
        ('W2', 'Fortnightly'),
        ('W4', '4 Weekly'),
        ('M1', 'Monthly'),
        ('M3', 'Quarterly'),
        ('MA', 'Bi-annually'),
        ('IO', 'One-off'),
        ('IR', 'Irregular')
    ], string='Pay Frequency', index=True, default='M1', help="Payment frequency towards HMRC.")
