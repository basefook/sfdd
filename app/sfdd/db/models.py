import re
import sqlalchemy as sa

from stemming.porter2 import stem
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Company(Base):
    __tablename__ = 'companies'

    CORPORATE_SUFFIXES = {'llc', 'llp', 'corp', 'inc', 'ltd', 'spa', 'co', 'lp'}

    _id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    key = sa.Column(sa.String, index=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)
        self.key = ''.join(stem(s) for s in self.name.split())


class URL(Base):
    __tablename__ = 'urls'

    _id = sa.Column(sa.Integer, primary_key=True)
    domain = sa.Column(sa.String, index=True)
    path = sa.Column(sa.String)


class CompanyURL(Base):
    __tablename__ = 'company_urls'

    url_id = sa.Column(sa.Integer, sa.ForeignKey(URL._id), primary_key=True)
    company_id = sa.Column(sa.Integer, sa.ForeignKey(Company._id), primary_key=True)
