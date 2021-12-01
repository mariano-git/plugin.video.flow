import inspect
import types
from inspect import Signature
from pprint import pprint
from typing import Any

from ext.util import SingletonMeta


class ApiModel:
    def __init__(self):
        self.apiModel = {}

    def get(self, node, key, create: bool = False):
        if key not in node:
            return None
        return node[key]

    def put(self, node, key: str, value: Any):
        if key not in node:
            node[key] = value
        return node[key]

    def getApi(self, apiName: str):
        return self.apiModel[apiName]

    def dump(self):
        pprint(self.apiModel)

    def _arguments(self, args: dict, key: str, annotation: Any, default: Any):
        _type_ = type(annotation).__name__
        if _type_ == 'type':
            # this is surely a class, so it's a Schema and should be the only one
            _type_ = 'Schema'
            _as_ = f"{annotation.__module__}.{annotation.__name__}"
        elif _type_ == 'BeanParam':
            # Special case when have mixed parameters, this one goes in body
            _as_ = None
        else:
            _as_ = annotation.kwargs['name']

        if _type_ not in args:
            args[_type_] = []

        args[_type_].append({'name': key, 'as': _as_, 'default': default if default is not Signature.empty else None})

    def registerCall(self, decorator, target):
        annotations = inspect.signature(target)
        fnc = target.__name__
        cls = target.__qualname__.replace('.' + fnc, '')
        clsNode = self.put(self.apiModel, cls, {})
        fncNode = self.put(clsNode, fnc, {})
        request = self.put(fncNode, 'request', {})
        response = self.put(fncNode, 'response', {})

        parameters = {}
        if annotations is not None:
            params = annotations.parameters
            for name in params:
                if name != 'self':
                    param = params[name]
                    self._arguments(parameters, name, param.annotation, param.default)
            self.put(request, 'parameters', parameters)
            return_type = annotations.return_annotation
            self.put(response, 'type', return_type)
        _type_ = type(decorator).__name__.lower()
        # FIXME
        if _type_ == 'post' or _type_ == 'get':
            self.put(fncNode, 'method', _type_)
        else:
            self.put(fncNode, _type_, decorator.arg)

    def registerApi(self, decorator, target):
        # this is special for some decorators

        cls = target.__name__
        clsNode = self.get(self.apiModel, cls)
        _type_ = type(decorator).__name__.lower()
        self.put(clsNode, _type_, decorator.arg)


class RuntimeDelegate(metaclass=SingletonMeta):

    def __init__(self):
        self.apimodel = ApiModel()

    def register(self, decorator, callable, args):

        if isinstance(callable, types.FunctionType):
            self.apimodel.registerCall(decorator=decorator, target=callable)
        elif inspect.isclass(callable):
            self.apimodel.registerApi(decorator=decorator, target=callable)

    def dump(self):
        self.apimodel.dump()
