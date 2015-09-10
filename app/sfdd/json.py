import jsl

from jsonschema import (
    ValidationError as JsonValidationError,
    validate as validate_json
)


class json_body(object):
    memoized_schemas = {}
    def __init__(self, doc_class, role=None):
        self.doc_class = doc_class
        self.role = role

    def __call__(self, func):
        doc_class = self.doc_class
        role = self.role

        def json_validator(self):
            try:
                key = doc_class.__name__ + role
                json_schema = json_body.memoized_schemas.get(key)
                if not json_schema:
                    json_schema = doc_class.get_schema(role=role)
                    json_body.memoized_schemas[key] = json_schema
                validate_json(self.request.json, json_schema)
            except ValueError:
                raise Exception  # TODO: raise proper API exception
            except JsonValidationError:
                raise Exception  # TODO raise proper API exception
            return func(self)
        json_validator.__name__ = func.__name__
        return json_validator


class json_schemas(object):
    class CompanyJsonSchema(jsl.Document):
        name = jsl.StringField(required=True)
        url = jsl.StringField(required=False)
        state = jsl.StringField(required=False)
        city = jsl.StringField(required=False)
        postal_code = jsl.StringField(required=False)
