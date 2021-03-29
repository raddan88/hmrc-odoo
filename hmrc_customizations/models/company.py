from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import requests
import logging

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = 'res.company'

    hmrc_aoref = fields.Char("Accounts Office Reference")
    hmrc_cotaxref = fields.Char("COTAX Reference")

    # Not Needed for RTI endpoint. They will be needed for the future MTD submissions (via REST API)
    # hmrc_client_id = fields.Char("Client Id")
    # hmrc_client_secret = fields.Char('Secret')
    # hmrc_access_token = fields.Char("OAuth2 Access Token", readonly=True)
    # hmrc_refresh_token = fields.Char("OAuth2 Refresh Token", readonly=True)
    # hmrc_last_refreshed = fields.Datetime(
    #     string='OAuth2 Last Refresh Date', readonly=True)
    # hmrc_expiration_date = fields.Datetime(
    #     string='OAuth2 Expiration Date', readonly=True)

    # def authorize(self):
    #     if not self.hmrc_client_id or not self.hmrc_client_id:
    #         raise ValidationError("You have to fill all fields.")

    #     base_url = self.env['ir.config_parameter'].get_param('web.base.url')
    #     hmrc_web_url = self.env['ir.config_parameter'].get_param('hmrc_web_base_url')
    #     auth_url = f"""{hmrc_web_url}/oauth/authorize?response_type=code&state={self.id}&client_id={self.hmrc_client_id}&scope=hello&redirect_uri={base_url}/hmrc/oauth/callback"""

    #     return {
    #         "type": "ir.actions.act_url",
    #         "url": auth_url,
    #         "target": "new",
    #     }

    # def check_connectivity(self):
    #     hmrc_api_base_url = self.env['ir.config_parameter'].get_param(
    #         'hmrc_api_base_url')
        
    #     if self.hmrc_expiration_date < datetime.now():
    #         _logger.info(
    #             f'[HMRC] Refresh OAuth access token for company {self.name}')
    #         response = requests.post(f'{hmrc_api_base_url}/oauth/token',
    #                                  data={
    #                                      "client_secret": self.hmrc_client_secret,
    #                                      "client_id": self.hmrc_client_id,
    #                                      "grant_type": "refresh_token",
    #                                      "refresh_token": self.hmrc_refresh_token
    #                                  })
    #         if response.status_code is not 200:
    #             message = f'[HMRC] Error during access token refresh: invalid response, status code: {response.status_code}, content: {response.text}'
    #             _logger.error(message)
    #             raise ValidationError(message)

    #         responseJson = response.json()
    #         expiryDate = datetime.now() + \
    #             timedelta(seconds=responseJson["expires_in"])
    #         self.write({
    #             'hmrc_access_token': responseJson["access_token"],
    #             'hmrc_refresh_token': responseJson["refresh_token"],
    #             'hmrc_last_refreshed': datetime.now(),
    #             'hmrc_expiration_date': expiryDate
    #         })
    #         _logger.info(
    #             f'[HMRC] Successful token refresh for company {self.name}, expiry date is {expiryDate}')

    #     response = requests.get(f'{hmrc_api_base_url}/hello/user',
    #         headers={
    #             "Accept":f"application/vnd.hmrc.1.0+json",
    #             "Authorization":f"Bearer {self.hmrc_access_token}"})

    #     if response.status_code is not 200:
    #         message = f'[HMRC] Error during connectivity test: invalid response, status code: {response.status_code}, content: {response.text}'
    #         _logger.error(message)
    #         raise ValidationError(message)
    
        
    #     return self.env['erpify.notifications.message.wizard'].show_success(f'Company {self.name} is successfully connected to HMRC')

        