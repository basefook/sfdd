import sqlalchemy as sa

from pyramid.view import view_config, view_defaults

from sfdd.db.models import Company
from sfdd.constants import SUCCESS
from sfdd.contexts import CompanyContext
from sfdd.json import json_body, json_schemas


class View(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context


@view_defaults(renderer='json', route_name='companies')
class CompaniesView(View):

    @view_config(request_method='GET')
    def search_companies(self):
        limit = self.request.GET.get('limit', 25)
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

    @view_config(request_method='POST')
    @json_body(json_schemas.CompanyJsonSchema, role='creator')
    def insert_company(self):
        json_body = self.request.json
        company = Company(name=json_body['name'],
                          url=json_body.get('url'),
                          state=json_body.get('state'),
                          city=json_body.get('city'),
                          postal_code=json_body.get('postal_code'))
        self.request.db_session.add(company)
        return SUCCESS

    @staticmethod
    def find_matches(db_session, src, limit):
        name_similarity = sa.func.similarity(src.name, Company.name)\
            .label('name')
        url_similarity = sa.func.similarity(src.url, Company.url)\
            .label('url')
        loc_similarity = sa.func.similarity(src.loc_key, Company.loc_key)\
            .label('loc')
        ave_similarity = (
            (name_similarity + url_similarity + loc_similarity) / 3.0)\
            .label('ave')
        query = db_session\
            .query(Company._id.label('company_id'),
                   Company.name.label('company_name'),
                   ave_similarity,
                   name_similarity,
                   url_similarity,
                   loc_similarity)\
            .order_by(ave_similarity.desc(),
                      name_similarity.desc(),
                      url_similarity.desc(),
                      loc_similarity.desc())\
            .limit(limit)
        matches = []
        for rec in query:
            matches.append({
                'id': rec.company_id,
                'name': rec.company_name,
                'score': {
                    'name': rec.name,
                    'url': rec.url,
                    'location': rec.loc,
                    'average': rec.ave,
                },
            })
        return matches

@view_defaults(renderer='json', route_name='company', context=CompanyContext)
class CompanyView(View):

    @view_config(request_method='GET')
    def get_company(self):
        return SUCCESS

    @view_config(request_method='PATCH')
    def update_company(self):
        return SUCCESS

    @view_config(request_method='DELETE')
    def delete_company(self):
        return SUCCESS


def includeme(config):
    routes = [
        ('companies', '/companies'),
        ('company', '/companies/{company_id:\d+}'),
    ]
    for name, pattern in routes:
        config.add_route(name, pattern)
