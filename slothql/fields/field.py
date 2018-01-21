import inspect
from functools import partial
from typing import Union, Type

import graphql
from graphql.type.definition import GraphQLType

from .list import ListMixin


def is_method(func):
    return func.__code__.co_varnames and 'self' == func.__code__.co_varnames[0]


class Field(ListMixin, graphql.GraphQLField):
    def get_resolver(self, resolver):
        if resolver is None:
            return self.default_resolver
        if isinstance(resolver, staticmethod):
            return resolver.__func__
        if isinstance(resolver, classmethod):
            return partial(resolver.__func__, type(self))
        if is_method(resolver):
            return partial(resolver, self)
        return resolver

    @property
    def default_resolver(self):
        return self.resolve_field

    def __init__(self, of_type: Union[GraphQLType, Type[GraphQLType]], resolver=None, **kwargs):
        of_type = of_type() if inspect.isclass(of_type) else of_type
        assert isinstance(of_type, GraphQLType), f'"of_type" needs to be a valid GraphQlType'

        resolver = self.get_resolver(resolver)
        assert callable(resolver), f'resolver needs to be callable, not {resolver}'

        super().__init__(type=of_type, resolver=partial(self.resolve, resolver), **kwargs)

    @classmethod
    def resolve(cls, resolver, obj, info: graphql.ResolveInfo):
        if not obj and resolver is None:
            return None
        return resolver(obj, info)

    def __repr__(self) -> str:
        return f'<Field: {repr(self.type)}>'

    @classmethod
    def resolve_field(cls, obj, info: graphql.ResolveInfo):
        if obj is None:
            return None
        name = info.field_name
        if isinstance(obj, dict):
            value = obj.get(name)
        else:
            value = getattr(obj, name, None)
        return value() if callable(value) else value
