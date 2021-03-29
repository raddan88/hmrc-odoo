from odoo import api, fields, models, tools, _
import logging
_logger = logging.getLogger(__name__)


class TaxSystem(models.Model):
    _name = 'res.tax.system'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)


class Company(models.Model):
    _inherit = 'res.company'

    tax_system_id = fields.Many2one('res.tax.system', 'Tax System', required=True)
    tax_system_code = fields.Char(compute='_compute_tax_system_code', store=True)

    @api.depends('tax_system_id')
    def _compute_tax_system_code(self):
        for record in self:
            record.tax_system_code = record.tax_system_id.code
