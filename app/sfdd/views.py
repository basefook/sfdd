import re
import urllib
import sqlalchemy as sa

from sfdd.db.models import Company, CompanyURL, URL
from sfdd.constants import SUCCESS
from sfdd.lib.view import View, json_body, api_defaults, api_config
from sfdd.json_schemas import CompanyBatchDocument


@api_defaults(route_name='companies')
class CompaniesView(View):

    @api_config(request_method='GET')
    def search_companies(self):
        limit = self.request.GET.get('limit', 10)
        theta = float(self.request.GET.get('theta', 0.0))
        matches = self.find_matches(
            self.request.db_session,
            Company(name=self.request.GET.get('name', '')),
            self.request.GET.get('url'),
            limit=limit,
            theta=theta)
        return {
            'matches': matches
        }

    @api_config(request_method='POST')
    @json_body(CompanyBatchDocument, role='creator')
    def insert_companies(self):
        for c in self.request.json['companies']:
            # normalize company name string
            company_name = re.sub(r'[^a-zA-Z0-9\s]', '', c['name'].lower())
            company_name = re.sub('\s+', ' ', company_name)
            company_name = ' '.join(s for s in company_name.split()
                                    if s not in Company.CORPORATE_SUFFIXES)

            # prepare URL for urlparse
            company_url = c.get('url', '')
            if company_url and (not re.match(r'https?://', company_url)):
                company_url = 'http://' + company_url

            # find or create company
            company = self.request.db_session.query(Company)\
                .filter_by(key=company_name)\
                .first()
            if not company:
                company = Company(name=company_name)
                self.request.db_session.add(company)
                self.request.db_session.flush()

            # insert company and url data
            url_id = None
            if company_url:
                domain_name, path = self.extract_domain_and_path(company_url)
                if domain_name:
                    data = self.request.db_session\
                        .query(URL._id, CompanyURL)\
                        .outerjoin(CompanyURL,
                                   sa.and_(CompanyURL.url_id == URL._id,
                                           CompanyURL.company_id == company._id))\
                        .filter(URL.domain == domain_name)\
                        .first()
                    url_id, company_url = data if data else (None, None)
                    if not url_id:
                        url_rec = URL(domain=domain_name, path=path)
                        self.request.db_session.add(url_rec)
                        self.request.db_session.flush()
                        url_id = url_rec._id
                    if not company_url:
                        self.request.db_session.add(
                            CompanyURL(url_id=url_id, company_id=company._id))
        return SUCCESS

    @classmethod
    def extract_domain_and_path(cls, url):
        try:
            parsed = urllib.parse.urlparse(url)
            domain_name = parsed.netloc.lower().lstrip('www.')
            return (domain_name, parsed.path)
        except ValueError:
            # TODO: log this
            return (None, None)

    @classmethod
    def find_matches(cls, db_session, src, url, limit=10, theta=0.0):
        compare_names = (src.name and src.name is not None)
        compare_urls = (url and url is not None)

        projection = [
            Company._id.label('company_id'),
            Company.name.label('company_name'),
        ]

        similarities = []
        order_by = []

        if compare_names:
            name_similarity = sa.func.similarity(src.key, Company.key).label('name_score')
            projection.append(name_similarity)
            similarities.append(name_similarity)
            order_by.append(name_similarity.desc())

        if compare_urls:
            domain_name, _ = cls.extract_domain_and_path(url)
            if domain_name:
                url_similarity = sa.case([(URL.domain == domain_name, 1)], else_=0).label('url_score')
                projection.append(url_similarity)
                projection.append(URL.domain.label('domain_name'))
                similarities.append(url_similarity)
                order_by.append(url_similarity.desc())
            else:
                compare_urls = False

        if not similarities:
            raise Exception('name or url query params missing')

        ave_similarity = (sum(similarities) / len(similarities)).label('ave_score')
        projection.append(ave_similarity)

        query = db_session.query(*projection)
        if compare_urls:
            query = query\
                .outerjoin(CompanyURL, CompanyURL.company_id == Company._id)\
                .outerjoin(URL, sa.and_(URL._id == CompanyURL.url_id,
                                        URL.domain == domain_name))
        query = query\
            .filter(ave_similarity > theta)\
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
                'url': rec.domain_name if (compare_urls and rec.domain_name) else None,
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
