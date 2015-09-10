import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Company(Base):
    __tablename__ = 'companies'

    _id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, index=True, nullable=False)
    url = sa.Column(sa.String, index=True, default='')
    loc_key = sa.Column(sa.String, index=True)
    state = sa.Column(sa.String, default='')
    city = sa.Column(sa.String, default='')
    postal_code = sa.Column(sa.String, default='')

    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)
        self.loc_key = self.build_loc_key(self.state,
                                          self.city,
                                          self.postal_code)

    @staticmethod
    def build_loc_key(state=None, city=None, postal_code=None):
        return '{}{}{}'.format(state or '_',
                               city or '_',
                               postal_code or '_')\
            .lower()\
            .replace(' ', '')
