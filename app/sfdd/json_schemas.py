from __future__ import absolute_import

import jsl

from sfdd.collections import enum


ROLES = enum('CREATOR')


# variables
true_if_creator = jsl.Var({ROLES.CREATOR: True})


# documents
class BaseDocument(jsl.Document):
    pass


class CompanyDocument(BaseDocument):
    name = jsl.StringField(required=true_if_creator)
    url = jsl.StringField(required=False)
    state = jsl.StringField(required=False)
    city = jsl.StringField(required=False)
    postal_code = jsl.StringField(required=False)
    account_id = jsl.StringField(required=true_if_creator)
    company_id = jsl.StringField(required=true_if_creator)


class CompanyBatchDocument(BaseDocument):
    companies = jsl.ArrayField(jsl.DocumentField(CompanyDocument, required=True))
