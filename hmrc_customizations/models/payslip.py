from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import lxml.etree as ET
import lxml.objectify as objectify
import hashlib
import base64
import uuid

import requests
import logging

_logger = logging.getLogger(__name__)


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    hmrc_correlation_id = fields.Char('HMRC Tax Code', readonly=True)

    def send_to_hmrc(self):
        _logger.info('Send payslip to HMRC')
        xml = self._construct_submission_request()

        response = requests.post(f"{self.env['ir.config_parameter'].get_param('hmrc_rti_base_url')}/submission",
                                 data=xml,
                                 headers={
                                     "Content-Type": "application/xml",
                                 })

        if response.status_code != 200:
            _logger.error(f'Error during FPS submission, status_code {response.status_code}')
            return None

        responseXml = objectify.fromstring(response.content)
        self.hmrc_correlation_id = responseXml.Header.MessageDetails.CorrelationID
        return self.env['erpify.notifications.message.wizard'].show_success(f"Request has been successfully submitted. Correlation ID: {self.hmrc_correlation_id}")

    def poll_hmrc_submission_status(self):
        if self.hmrc_correlation_id is None:
            raise ValidationError('Missing correlation id - you have to submit the payslip first!')

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<GovTalkMessage xmlns="http://www.govtalk.gov.uk/CM/envelope">
    <EnvelopeVersion>2.0</EnvelopeVersion>
    <Header>
        <MessageDetails>
            <Class>HMRC-PAYE-RTI-FPS</Class>
            <Qualifier>poll</Qualifier>
            <Function>submit</Function>
            <CorrelationID>{self.hmrc_correlation_id}</CorrelationID>
            <Transformation>XML</Transformation>
        </MessageDetails>
    </Header>
    <GovTalkDetails>
        <Keys/>
    </GovTalkDetails>
</GovTalkMessage>"""

        response = requests.post(f"{self.env['ir.config_parameter'].get_param('hmrc_rti_base_url')}/poll",
                                 data=xml,
                                 headers={
                                     "Content-Type": "application/xml",
                                 })

        if response.status_code != 200:
            _logger.error(f'Error during FPS poll, status_code {response.status_code}')
            return None

        return self.env['erpify.notifications.message.wizard'].show_success(response.text)

    def _construct_submission_request(self):
        config = self.env['ir.config_parameter']

        # TODO remove Timestamp tag and future reference date for production
        # referenceDate = datetime.now()
        referenceDate = datetime(2022, 3, 20)
        currentYearTaxYearEnd = datetime(referenceDate.year, 4, 5)
        periodEnd = currentYearTaxYearEnd
        if currentYearTaxYearEnd < referenceDate:
            periodEnd = datetime(referenceDate.year+1, 4, 5)

        #####################################################
        # TODO set these values accordingly in EIR integration
        ######################################################
        payslip_id = self.number
        # leave it on None if leave date is empty
        leaving_date = None
        # Taxable pay to date in this employment including taxable benefits undertaken through payroll
        taxable_pay_to_date = 99999
        # Total tax to date in this employment including this submission
        total_tax_to_date = 111111
        # Taxable pay in this payment - not necessarily the contract wage
        taxable_pay = self.contract_id.wage
        # Payment date probably will be different than the payslip creation date
        payment_date = referenceDate

        # Normal Hours worked - should be calculated from the paid period, and turned into an enum value:
        # A Up to 15.99 hours
        # B 16 to 23.99 hours
        # C 24 to 29.99 hours
        # D 30 hours or more
        # E Other
        hours_worked = 'B'

        # Tax deducted or refunded from this payment
        tax_deducted = 0
        ########################################################

        messageBody = f"""<Body xmlns="http://www.govtalk.gov.uk/CM/envelope">
		<IRenvelope xmlns="http://www.govtalk.gov.uk/taxation/PAYE/RTI/FullPaymentSubmission/21-22/1">
			<IRheader>
				<Keys>
					<Key Type="TaxOfficeNumber">{config.get_param('hmrc_tax_office_number')}</Key>
					<Key Type="TaxOfficeReference">{config.get_param('hmrc_tax_office_reference')}</Key>
				</Keys>
				<PeriodEnd>{periodEnd.strftime("%Y-%m-%d")}</PeriodEnd>
				<DefaultCurrency>GBP</DefaultCurrency>
				<Sender>Employer</Sender>
			</IRheader>
			<FullPaymentSubmission>
				<EmpRefs>
					<OfficeNo>{config.get_param('hmrc_tax_office_number')}</OfficeNo>
					<PayeRef>{config.get_param('hmrc_tax_office_reference')}</PayeRef>
					<AORef>{self.employee_id.company_id.hmrc_aoref}</AORef>
					<COTAXRef>{self.employee_id.company_id.hmrc_cotaxref}</COTAXRef>
				</EmpRefs>
				<RelatedTaxYear>21-22</RelatedTaxYear>
				<Employee>
					<EmployeeDetails>
						<NINO>{self.employee_id.hmrc_nino}</NINO>
						<Name>
							<Fore>{self.employee_id.forename}</Fore>
							<Sur>{self.employee_id.surname}</Sur>
						</Name>
						<BirthDate>{self.employee_id.birthday}</BirthDate>
						<Gender>{'F' if self.employee_id.gender == 'female' else 'M'}</Gender>
					</EmployeeDetails>
					<Employment>
						<OffPayrollWorker>yes</OffPayrollWorker>
						<PayId>{payslip_id}</PayId>
						{f'<LeavingDate>{leaving_date.strftime("%Y-%m-%d")}</LeavingDate>' if leaving_date is not None else ''}
						<FiguresToDate>
							<TaxablePay>{taxable_pay_to_date:.2f}</TaxablePay>
							<TotalTax>{total_tax_to_date:.2f}</TotalTax>
						</FiguresToDate>
						<Payment>
							<BacsHashCode>{uuid.uuid4().hex}{uuid.uuid4().hex}</BacsHashCode>
							<PayFreq>{self.contract_id.hmrc_schedule_pay}</PayFreq>
							<PmtDate>{payment_date.strftime("%Y-%m-%d")}</PmtDate>
							<MonthNo>{payment_date.month}</MonthNo>
							<PeriodsCovered>1</PeriodsCovered>
							<HoursWorked>{hours_worked}</HoursWorked>
							<TaxCode>{self.contract_id.hmrc_tax_code}</TaxCode>
							<TaxablePay>{taxable_pay:.2f}</TaxablePay>
							<TaxDeductedOrRefunded>{tax_deducted:.2f}</TaxDeductedOrRefunded>
						</Payment>
					</Employment>
				</Employee>
			</FullPaymentSubmission>
		</IRenvelope>
	</Body>"""

        xmlTree = ET.fromstring(messageBody)
        canonizedXml = ET.tostring(xmlTree, method="c14n")
        hash_obj = hashlib.sha1(canonizedXml)
        signature = base64.b64encode(hash_obj.digest()).decode('utf-8')

        fullMessage = f"""<?xml version="1.0" encoding="UTF-8"?>
<GovTalkMessage xmlns="http://www.govtalk.gov.uk/CM/envelope">
	<EnvelopeVersion>2.0</EnvelopeVersion>
	<Header>
		<MessageDetails>
			<Class>HMRC-PAYE-RTI-FPS</Class>
			<Qualifier>request</Qualifier>
			<Function>submit</Function>
			<CorrelationID />
			<Transformation>XML</Transformation>
		</MessageDetails>
		<SenderDetails>
			<IDAuthentication>
				<SenderID>{config.get_param('hmrc_sender_id')}</SenderID>
				<Authentication>
					<Method>clear</Method>
					<Role>principal</Role>
					<Value>{config.get_param('hmrc_sender_password')}</Value>
				</Authentication>
			</IDAuthentication>
		</SenderDetails>
	</Header>
	<GovTalkDetails>
		<Keys>
			<Key Type="TaxOfficeNumber">{config.get_param('hmrc_tax_office_number')}</Key>
			<Key Type="TaxOfficeReference">{config.get_param('hmrc_tax_office_reference')}</Key>
		</Keys>
		<TargetDetails>
			<Organisation>IR</Organisation>
		</TargetDetails>
		<ChannelRouting>
			<Channel>
				<URI>{config.get_param('hmrc_vendor_id')}</URI>
				<Product>Odoo</Product>
				<Version>13</Version>
			</Channel>
			<Timestamp>{periodEnd.strftime("%Y-%m-%dT12:00:00")}</Timestamp>
		</ChannelRouting>
	</GovTalkDetails>
	{messageBody.replace('<Body xmlns="http://www.govtalk.gov.uk/CM/envelope">','<Body>')
		.replace('</DefaultCurrency>',f'</DefaultCurrency><IRmark Type="generic">{signature}</IRmark>')}
</GovTalkMessage>"""

        return fullMessage
