from collections import namedtuple
from collections.abc import Iterable
from six import string_types
from itertools import chain
from inspect import signature
from sqlalchemy import and_, or_, not_, func

BooleanFunction = namedtuple(
    'BooleanFunction', ('key', 'sqlalchemy_fn', 'only_one_arg')
)
BOOLEAN_FUNCTIONS = [
    BooleanFunction('or', or_, False),
    BooleanFunction('and', and_, False),
    BooleanFunction('not', not_, True),
]
"""
Sqlalchemy boolean functions that can be parsed from the filter definition.
"""

class Operator(object):

    OPERATORS = {
        'is_null': lambda f: f.is_(None),
        'is_not_null': lambda f: f.isnot(None),
        '==': lambda f, a: f == a,
        'eq': lambda f, a: f == a,
        '!=': lambda f, a: f != a,
        'ne': lambda f, a: f != a,
        '>': lambda f, a: f > a,
        'gt': lambda f, a: f > a,
        '<': lambda f, a: f < a,
        'lt': lambda f, a: f < a,
        '>=': lambda f, a: f >= a,
        'ge': lambda f, a: f >= a,
        '<=': lambda f, a: f <= a,
        'le': lambda f, a: f <= a,
        'like': lambda f, a: f.like(a),
        'ilike': lambda f, a: f.ilike(a),
        'not_ilike': lambda f, a: ~f.ilike(a),
        'in': lambda f, a: f.in_(a),
        'not_in': lambda f, a: ~f.in_(a),
        'any': lambda f, a: f.any(a),
        'not_any': lambda f, a: func.not_(f.any(a)),
    }

    def __init__(self, operator=None):
        if not operator:
            operator = '=='

        if operator not in self.OPERATORS:
            raise Exception('Operator `{}` not valid.'.format(operator))

        self.operator = operator
        self.function = self.OPERATORS[operator]
        self.arity = len(signature(self.function).parameters)

class Filter(object):

    def __init__(self, filter_spec):
        self.filter_spec = filter_spec

        try:
            filter_spec['field']
        except KeyError:
            raise Exception('`field` is a mandatory filter attribute.')
        except TypeError:
            raise Exception(
                'Filter spec `{}` should be a dictionary.'.format(filter_spec)
            )

        self.operator = Operator(filter_spec.get('op'))
        # self.value = filter_spec.get('value')
        value_present = True if 'value' in filter_spec else False
        if not value_present and self.operator.arity == 2:
            raise Exception('`value` must be provided.')
        self.get_filter_value(filter_spec.get('value'))

    def get_filter_value(self, filter_value):
        # todo : sanitize value first
        self.value = filter_value
        if self.operator.operator == 'ilike':
            self.value = '%{}%'.format(filter_value)


    def get_named_models(self):
        if "model" in self.filter_spec:
            return {self.filter_spec['model']}
        return set()

    def format_for_sqlalchemy(self, model):
        # filter_spec = self.filter_spec
        operator = self.operator
        value = self.value

        # model = get_model_from_spec(filter_spec, query, default_model)

        function = operator.function
        arity = operator.arity

        field_name = self.filter_spec['field']
        sqlalchemy_field = getattr(model, field_name)
        # field = Field(model, field_name)
        # sqlalchemy_field = field.get_sqlalchemy_field()

        if arity == 1:
            return function(sqlalchemy_field)

        if arity == 2:
            return function(sqlalchemy_field, value)


class BooleanFilter(object):

    def __init__(self, function, *filters):
        self.function = function
        self.filters = filters

    def get_named_models(self):
        models = set()
        for filter in self.filters:
            models.update(filter.get_named_models())
        return models

    def format_for_sqlalchemy(self, model):
        return self.function(*[
            filter.format_for_sqlalchemy(model)
            for filter in self.filters
        ])

    # def format_for_sqlalchemy(self, query, default_model):
    #     return self.function(*[
    #         filter.format_for_sqlalchemy(query, default_model)
    #         for filter in self.filters
    #     ])


def _is_iterable_filter(filter_spec):
    """ `filter_spec` may be a list of nested filter specs, or a dict.
    """
    return (
        isinstance(filter_spec, Iterable) and
        not isinstance(filter_spec, (string_types, dict))
    )


def build_filters(filter_spec):
    """ Recursively process `filter_spec` """

    if _is_iterable_filter(filter_spec):
        return list(chain.from_iterable(
            build_filters(item) for item in filter_spec
        ))

    if isinstance(filter_spec, dict):
        # Check if filter spec defines a boolean function.
        for boolean_function in BOOLEAN_FUNCTIONS:
            if boolean_function.key in filter_spec:
                # The filter spec is for a boolean-function
                # Get the function argument definitions and validate
                fn_args = filter_spec[boolean_function.key]

                if not _is_iterable_filter(fn_args):
                    raise Exception(
                        '`{}` value must be an iterable across the function '
                        'arguments'.format(boolean_function.key)
                    )
                if boolean_function.only_one_arg and len(fn_args) != 1:
                    raise Exception(
                        '`{}` must have one argument'.format(
                            boolean_function.key
                        )
                    )
                if not boolean_function.only_one_arg and len(fn_args) < 1:
                    raise Exception(
                        '`{}` must have one or more arguments'.format(
                            boolean_function.key
                        )
                    )
                return [
                    BooleanFilter(
                        boolean_function.sqlalchemy_fn, *build_filters(fn_args)
                    )
                ]

    return [Filter(filter_spec)]