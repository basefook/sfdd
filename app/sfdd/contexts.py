from sfdd.db.models import Company


class BaseContext(object):
    def __init__(self, request):
        self.request = request
        self.db_session = request.db_session
        self.on_create()

    def on_create(self):
        pass


class CompanyContext(BaseContext):
    def on_create(self):
        company_id = self.request.matchdict['company_id']
        self.company = self.db_session.query(Company)\
            .filter(Company._id == company_id)\
            .first()
