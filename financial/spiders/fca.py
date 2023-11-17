import json
import math
from urllib.parse import urlparse, parse_qs

import scrapy
from scrapy import FormRequest
from scrapy.http import Response

import financial.constants as constants


class FcaSpider(scrapy.Spider):
    name = "fca"

    def __init__(self, keywords_list: dict[str, int], *args, **kwargs):
        self.keywords_list = keywords_list
        super().__init__()

    def start_requests(self):

        for url, max_results in self.keywords_list.items():
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            keyword = query_params.get('q')[0]
            max_pages = math.ceil(int(max_results) / constants.RESULTS_PER_PAGE) + 5

            search_params = [k.strip() for k in keyword.split(' ') if k.strip()]
            yield from self.get_next_page(search_params, 1, max_pages)

    def parse_pagination(self, response: Response, **kwargs):
        results = response.jmespath('actions[0].returnValue.accDetails').getall()

        if not results:
            return

        statuses_to_ignore = [
            'longer',
            'revoked',
            'unauthorised',
        ]

        for result in results:
            company_id = result.get('acc').get('Id')
            name = result.get('acc').get('Name')
            status = result.get('acc').get('ShPo_Registerstatus__c')

            if any([status_to_ignore in status.lower() for status_to_ignore in statuses_to_ignore]):
                continue

            details_message = constants.DETAILS_MESSAGE.copy()
            details_message['actions'][0]['params']['orgId'] = company_id

            yield FormRequest(url=constants.DETAILS_URL,
                              formdata=self.get_post_data(details_message),
                              cb_kwargs={
                                  'id': company_id,
                                  'name': name,
                                  'status': status,
                                  'keyword': kwargs.get('keyword'),
                              })
        max_pages = kwargs.get('max_pages')
        next_page = kwargs.get('page') + 1
        if next_page <= max_pages:
            yield from self.get_next_page(kwargs.get('keyword'), next_page, max_pages)

    def parse(self, response, **kwargs):
        result = response.jmespath('actions[0].returnValue').get()

        principal_data = result.get('principalAddress') or {}
        principal_address, principal_postcode, principal_phone, principal_email, principal_website = self.parse_address(principal_data)

        complaint_data = result.get('ComplaintContactAddress') or {}
        complaint_address, complaint_postcode, complaint_phone, complaint_email, complaint_website = self.parse_address(complaint_data)

        complaint_name = (result.get('ComplaintContact') or {}).get('Name') or ''

        yield {
            'company_url': f'https://register.fca.org.uk/s/firm?id={kwargs.get("id")}',
            'company_name': kwargs.get('name'),

            'complaint_name': complaint_name,
            'complaint_address': complaint_address,
            'complaint_postcode': complaint_postcode,
            'complaint_phone': complaint_phone or principal_phone,
            'complaint_email': complaint_email or principal_email,
            'complaint_website': complaint_website,

            'principal_address': principal_address,
            'principal_postcode': principal_postcode,
            'principal_phone': principal_phone,
            'principal_email': principal_email,
            'principal_website': principal_website,

            'status': kwargs.get('status'),
            'keyword': kwargs.get('keyword'),
        }

    def parse_address(self, address: dict[str, str]):
        address_lines = [v.strip() for k, v in address.items() if 'AddressLine' in k]
        postcode = address.get('ShGl_Postcode__c') or ''
        country_code = address.get('ShGl_PhoneCountryCode__c') or ''
        phone = address.get('ShGl_PhoneNumber__c') or ''
        if phone:
            phone = f'{country_code.strip()}{phone.strip()}'

        email = address.get('ShGl_EmailAddress__c') or ''
        website = address.get('ShGl_WebsiteAddress__c') or ''

        return ', '.join(address_lines), postcode.strip(), phone, email.strip(), website.strip()

    @staticmethod
    def get_post_data(message):
        return {
            'message': json.dumps(message),
            'aura.context': json.dumps(constants.CONTEXT),
            'aura.token': ''
        }

    def get_next_page(self, keyword: list, page: int, max_pages: int = 1):
        message = constants.MESSAGE.copy()

        message['actions'][0]['params']['pageNo'] = str(page)
        message['actions'][0]['params']['searchValues'] = keyword

        yield FormRequest(url=constants.PAGINATION_URL.format(page=page),
                          formdata=self.get_post_data(message),
                          callback=self.parse_pagination,
                          cb_kwargs={
                              'keyword': keyword,
                              'page': page,
                              'max_pages': max_pages
                          })
