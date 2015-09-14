import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Domain(Base):
    __tablename__ = 'domains'

    _id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=True, index=True)


class Company(Base):
    __tablename__ = 'companies'

    _id = sa.Column(sa.Integer, primary_key=True)
    account_id = sa.Column(sa.String)
    company_id = sa.Column(sa.String)
    name = sa.Column(sa.String, index=True, nullable=False)
    url = sa.Column(sa.String, index=True, default='')
    domain_id = sa.Column(sa.Integer, sa.ForeignKey(Domain._id), index=True)
    loc_key = sa.Column(sa.String, index=True)
    state = sa.Column(sa.String, default='')
    city = sa.Column(sa.String, default='')
    postal_code = sa.Column(sa.String, default='')

    domain = relationship(Domain, backref='companies')

    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)
        self.loc_key = '{}{}{}'\
            .format(self.state or '.',
                    self.city or '.',
                    self.postal_code or '.').lower().replace(' ', '')
