import urllib
import sqlalchemy as sa

from sfdd.db.models import Company, Domain
from sfdd.constants import SUCCESS
from sfdd.lib.view import View, json_body, api_defaults, api_config
from sfdd.json_schemas import CompanyBatchDocument


@api_defaults(route_name='companies')
class CompaniesView(View):

    @api_config(request_method='GET')
    def search_companies(self):
        limit = self.request.GET.get('limit', 10)
        matches = self.find_matches(
            self.request.db_session,
            Company(name=self.request.GET.get('name', ''),
                    url=self.request.GET.get('url', ''),
                    state=self.request.GET.get('state', ''),
                    city=self.request.GET.get('city', ''),
                    postal_code=self.request.GET.get('postal_code', '')),
            limit)
        return {
            'matches': matches
        }

    @api_config(request_method='POST')
    @json_body(CompanyBatchDocument, role='creator')
    def insert_companies(self):
        companies = []
        for company_json in self.request.json['companies']:
            domain = None
            url = company_json.get('url').lower()
            if url:
                domain_name = urllib.parse.urlparse(url).netloc.lower()
                domain = self.request.db_session.query(Domain)\
                    .filter_by(name=domain_name)
                if not domain:
                    domain = Domain(name=domain_name)
                    self.request.db_session.add(domain)
            company = Company(name=company_json['name'].lower(),
                              url=url,
                              state=company_json.get('state'),
                              city=company_json.get('city'),
                              postal_code=company_json.get('postal_code'))
            company.domain = domain
            companies.append(company)
        self.request.db_session.add_all(companies)
        return SUCCESS

    @staticmethod
    def find_matches(db_session, src, limit):
        compare_names = (src.name and src.name is not None)
        compare_urls = (src.url and src.url is not None)

        projection = [
            Company._id.label('company_id'),
            Company.name.label('company_name'),
            Company.account_id.label('company_account_id'),
            Company.company_id.label('company_company_id'),
        ]

        similarities = []
        order_by = []

        if compare_names:
            name_similarity = sa.func.similarity(src.name.lower(), Company.name).label('name_score')
            projection.append(name_similarity)
            similarities.append(name_similarity)
            order_by.append(name_similarity.desc())

        if compare_urls:
            url_similarity = sa.func.similarity(src.url, Company.url).label('url_score')
            projection.append(url_similarity)
            similarities.append(url_similarity)
            order_by.append(url_similarity.desc())

        if not similarities:
            raise Exception('name or url query params missing')

        ave_similarity = (sum(similarities) / len(similarities)).label('ave_score')
        projection.append(ave_similarity)

        query = db_session\
            .query(*projection)\
            .order_by(ave_similarity.desc(), *order_by)\
            .limit(limit)

        matches = []
        for rec in query:
            score = {
                'ave': round(rec.ave_score, 3),
            }
            if compare_names:
                score['name'] = round(rec.name_score, 3)
            if compare_urls:
                score['url'] = round(rec.url_score, 3)
            matches.append({
                'id': rec.company_id,
                'account_id': rec.company_account_id,
                'company_id': rec.company_company_id,
                'name': rec.company_name,
                'score': score,
            })
        return matches


@api_defaults(route_name='company')
class CompanyView(View):

    @api_config(request_method='GET')
    def get_company(self):
        return SUCCESS

    @api_config(request_method='PATCH')
    def update_company(self):
        return SUCCESS

    @api_config(request_method='DELETE')
    def delete_company(self):
        return SUCCESS
