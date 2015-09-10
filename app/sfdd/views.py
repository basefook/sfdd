import re
import sqlalchemy as sa

from sfdd.db.models import Company, CompanyURL, URL, SalesforceAccount
from sfdd.lib.view import View, json_body, api_defaults, api_config  # noqa


@api_defaults(route_name='companies')
class CompaniesView(View):

    @api_config(request_method='GET')
    def search_companies(self):
        limit = self.request.GET.get('limit', 10)
        theta = float(self.request.GET.get('theta', 0.0))
        company_url = self.request.GET.get('url', '')
        if company_url and (not re.match(r'https?://', company_url)):
            company_url = 'http://' + company_url

        company_name = self.request.GET.get('name', '')
        company_name = re.sub(r'[^a-zA-Z0-9\s]', '', company_name.lower())
        company_name = re.sub('\s+', ' ', company_name)
        company_name = ' '.join(s for s in company_name.split()
                                if s not in Company.CORPORATE_SUFFIXES)

        return self.find_matches(
            self.request.db_session,
            Company(name=company_name),
            company_url,
            limit=limit,
            theta=theta)

    @classmethod
    def find_matches(cls, db_session, src, url, limit=10, theta=0.0):
        compare_names = (src.name and src.name is not None)
        compare_urls = (url and url is not None)

        projection = [
            Company.name.label('company_name'),
            URL.domain.label('domain_name'),
            SalesforceAccount.account_id.label('account_id'),
            SalesforceAccount.case_safe_id.label('case_safe_id'),
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
                similarities.append(url_similarity)
                order_by.append(url_similarity.desc())
            else:
                compare_urls = False

        if not similarities:
            raise Exception('name or url query params missing')

        ave_similarity = (sum(similarities) / len(similarities)).label('ave_score')
        projection.append(ave_similarity)

        query = db_session.query(*projection)\
            .join(SalesforceAccount, SalesforceAccount.dimension_id == Company.dimension_id)\
            .outerjoin(CompanyURL, CompanyURL.company_id == Company._id)\
            .outerjoin(URL, URL._id == CompanyURL.url_id)\
            .filter(ave_similarity > theta)\
            .order_by(ave_similarity.desc(), *order_by)\
            .limit(limit)

        matches = []
        for rec in query:
            score = {
                'average': round(rec.ave_score, 3),
            }
            if compare_names:
                score['name'] = round(rec.name_score, 3)
            if compare_urls:
                score['url'] = round(rec.url_score, 3)
            matches.append({
                'account_id': rec.account_id,
                'case_safe_id': rec.case_safe_id,
                'url': rec.domain_name if rec.domain_name else None,
                'name': rec.company_name,
                'score': score,
            })
        return {
            'matches': matches
        }
