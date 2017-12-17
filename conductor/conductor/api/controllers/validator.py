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

from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class UniqueKeyLoader(Loader):
    """Unique Key Loader for PyYAML

    Ensures no duplicate keys on any given level.

    https://gist.github.com/pypt/94d747fe5180851196eb#gistcomment-2084028
    """

    DUPLICATE_KEY_PROBLEM_MARK = "found duplicate key"

    def construct_mapping(self, node, deep=False):
        """Check for duplicate keys while constructing a mapping."""
        if not isinstance(node, MappingNode):
            raise ConstructorError(
                None, None, "expected a mapping node, but found %s" % node.id,
                node.start_mark)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except (TypeError) as exc:
                raise ConstructorError("while constructing a mapping",
                                       node.start_mark,
                                       "found unacceptable key (%s)" % exc,
                                       key_node.start_mark)
            # check for duplicate keys
            if key in mapping:
                raise ConstructorError("while constructing a mapping",
                                       node.start_mark,
                                       self.DUPLICATE_KEY_PROBLEM_MARK,
                                       key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping
