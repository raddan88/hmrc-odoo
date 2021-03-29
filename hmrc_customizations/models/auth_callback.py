from odoo import http
from odoo.http import Response
from datetime import datetime, timedelta
import json
import requests
import logging

_logger = logging.getLogger(__name__)


class OAuthCallback(http.Controller):

    @http.route('/hmrc/oauth/callback', auth='public', methods=['GET'])
    def oauth_callback(self, ** kwargs):
        _logger.info(f'HMRC OAuth2 Callback received. State parameter: {kwargs["state"]}')
        
        if 'error' in kwargs:
            _logger.error(f'[HMRC] Error during authentication: {kwargs["error_code"]}: {kwargs["error_description"]}')
        elif 'code' in kwargs:
            company = http.request.env['res.company'].browse(int(kwargs["state"]))
            _logger.info(f'[HMRC] Requesting authorisation token for company {company.name}')
                
            hmrc_api_base_url = http.request.env['ir.config_parameter'].get_param('hmrc_api_base_url')
            web_base_url = http.request.env['ir.config_parameter'].get_param('web.base.url')        
            response = requests.post(f'{hmrc_api_base_url}/oauth/token',
                                    data={
                                        "client_secret": company.hmrc_client_secret,
                                        "client_id": company.hmrc_client_id,
                                        "grant_type": "authorization_code",
                                        "redirect_uri": f'{web_base_url}/hmrc/oauth/callback',
                                        "code": kwargs['code']
                                    })
            
            if response.status_code is not 200:
                _logger.error(f'[HMRC] Error during authentication: invalid response, status code: {response.status_code}, content@ {response.text}')
            else:
                responseJson = response.json()                
                expiryDate = datetime.now() + timedelta(seconds=responseJson["expires_in"])
                company.write({                    
                    'hmrc_access_token': responseJson["access_token"],
                    'hmrc_refresh_token': responseJson["refresh_token"],
                    'hmrc_last_refreshed': datetime.now(),
                    'hmrc_expiration_date': expiryDate
                })

                _logger.info(f'[HMRC] Successful authorisation of company {company.name}, expiry date is {expiryDate}')
        else:
            _logger.error(f'[HMRC] Error during authentication: missing code parameter')

        return json.dumps({"message":"Successful Authentication. You can close this tab now."})
