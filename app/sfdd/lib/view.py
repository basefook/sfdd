import pyramid.view

from jsonschema import (
    ValidationError as JsonValidationError,
    validate as validate_json
)


class View(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context


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


def api_defaults(*args, **kwargs):
    return pyramid.view.view_defaults(renderer='json', *args, **kwargs)


def api_config(*args, **kwargs):
    return pyramid.view.view_config(*args, **kwargs)
