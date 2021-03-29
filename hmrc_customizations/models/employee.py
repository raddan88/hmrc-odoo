from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class Employee(models.Model):
    _inherit = 'hr.employee'

    hmrc_nino = fields.Char("NI Number", help="National Insurance Number")

    # The equivalent of these 2 fields are already existing in EIR, you can remove them during integration
    surname = fields.Char()
    forename = fields.Char()
