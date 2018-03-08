# Copyright 2017 Francesco Ceccon
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import abc


class Dispatcher(object):
    def __init__(self, lookup, allow_missing=False):
        self._lookup = lookup
        self._allow_missing = allow_missing

    def dispatch(self, expr):
        type_ = type(expr)
        cb = self._lookup.get(type_)
        if cb is not None:
            return cb(expr)

        # try superclasses, for most cases this will work fine
        # but since dicts are not ordered it could cause
        # unexpected behaviour
        for target_type, cb in self._lookup.items():
            if isinstance(expr, target_type):
                return cb(expr)

        if not self._allow_missing:
            raise RuntimeError('Could not find callback for {} of type {}'.format(expr, type_))


class Visitor(object, metaclass=abc.ABCMeta):
    def __init__(self):
        self._registered_handlers = self.register_handlers()

    @abc.abstractmethod
    def register_handlers(self):
        pass

    def visit(self, expr, ctx):
        type_ = type(expr)
        cb = self._registered_handlers.get(type_)
        if cb is not None:
            return cb(expr, ctx)

        # try superclasses, for most cases this will work fine
        # but since dicts are not ordered it could cause
        # unexpected behaviour
        for target_type, cb in self._registered_handlers.items():
            if isinstance(expr, target_type):
                return cb(expr, ctx)

    def __call__(self, expr, ctx):
        return self.visit(expr, ctx)


class ForwardVisitor(Visitor):
    def __call__(self, expr, ctx):
        result = self.visit(expr, ctx)
        if result is not None:
            ctx[expr] = result
        return result


class BackwardVisitor(Visitor):
    @abc.abstractmethod
    def handle_result(self, expr, result, ctx):
        pass

    def __call__(self, expr, ctx):
        result = self.visit(expr, ctx)
        if isinstance(result, dict):
            for k, v in result.items():
                self.handle_result(k, v, ctx)
        elif result is not None:
            raise RuntimeError('BackwardVisitor must return dict')
        return result
