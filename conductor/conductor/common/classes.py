#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#

"""Class Helpers"""

from conductor.i18n import _LE  # pylint: disable=W0212


def get_class(kls):
    """Returns a class given a fully qualified class name"""
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    mod = __import__(module)
    for comp in parts[1:]:
        mod = getattr(mod, comp)
    return mod


class abstractclassmethod(classmethod):  # pylint: disable=C0103,R0903
    """Abstract Class Method Decorator from Python 3.3's abc module"""

    __isabstractmethod__ = True

    def __init__(self, callable):  # pylint: disable=W0622
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)


class ClassPropertyDescriptor(object):  # pylint: disable=R0903
    """Supports the notion of a class property"""

    def __init__(self, fget, fset=None):
        """Initializer"""
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        """Get attribute"""
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        """Set attribute"""
        if not self.fset:
            raise AttributeError(_LE("Can't set attribute"))
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        """Setter"""
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def classproperty(func):
    """Class Property decorator"""
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)
