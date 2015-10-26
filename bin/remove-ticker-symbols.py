import re

from sfdd.db.util import quick_sessionmaker, scoped_session
from sfdd.db.models import Company


with scoped_session(quick_sessionmaker()) as db:
    pattern = r'\s(nasdaq|nyse)[a-z]+$'
    companies = db.query(Company).filter(Company.name.op('~')(pattern))
    for c in companies:
        clean_name = re.sub(pattern, '', c.name)
        print('{} -> {}'.format(c.name, clean_name))
