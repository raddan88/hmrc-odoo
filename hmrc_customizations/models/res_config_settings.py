from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'HMRC API Configuration Settings'

    # Not Needed for RTI endpoint. They will be needed for the future MTD submissions (via REST API)
    # hmrc_web_base_url = fields.Char("HMRC Web Base Url",
    #                                      config_parameter='hmrc_web_base_url',
    #                                      required=True,
    #                                      help="Url without trailing slash")
    # hmrc_api_base_url = fields.Char("HMRC API Base Url",
    #                              config_parameter='hmrc_api_base_url',
    #                              required=True,
    #                              help="Url without trailing slash")

    hmrc_rti_base_url = fields.Char("HMRC RTI Base Url",
                                 config_parameter='hmrc_rti_base_url',
                                 required=True,
                                 help="Url without trailing slash")
                                 
    hmrc_vendor_id = fields.Char("HMRC Vendor Id",
                                 config_parameter='hmrc_vendor_id',
                                 required=True,
                                 help="4 digit Vendor ID")

    hmrc_sender_id = fields.Char("HMRC Sender Id",
                                 config_parameter='hmrc_sender_id',
                                 required=True,
                                 help="Value for <SenderID> tag")

    hmrc_sender_password = fields.Char("HMRC Sender Password",
                                 config_parameter='hmrc_sender_password',
                                 required=True,
                                 help="HMRC Authentication password")

    hmrc_tax_office_number = fields.Char("HMRC Tax Office Number",
                                 config_parameter='hmrc_tax_office_number',
                                 required=True,
                                 help="As received from HMRC SDS Team")

    hmrc_tax_office_reference = fields.Char("HMRC Tax Office Reference",
                                 config_parameter='hmrc_tax_office_reference',
                                 required=True,
                                 help="As received from HMRC SDS Team")
