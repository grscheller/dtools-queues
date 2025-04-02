# Copyright 2023-2025 Geoffrey R. Scheller
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

"""
### Data node class used privately by class SplitEnd

Node classes used with graph-like data structures. API designed to be used by
other data structures which contain these data structures.

"""

from __future__ import annotations
from collections.abc import Callable, Iterator
from typing import cast, TypeVar
from dtools.fp.err_handling import MB

D = TypeVar('D')  # Not needed for mypy, hint for pdoc.
T = TypeVar('T')


class SENode[D]:
    """Data node for class SplitEnd

    - data node for a top-to-root singularly linked list.
    - designed so multiple splitends can safely share the same data
    - this type of node always
      - contain data
      - potential link to previous node
    - nodes point towards a unique "bottom node" with no predecessor
      - in a Boolean context returns true if not at the bottom
      - multiple bottom nodes can exist
    - two nodes compare as equal if
      - both their previous Nodes are the same
      - their data compares as equal
    - more than one node can point to the same proceeding node
      - forming bush like graphs

    """

    __slots__ = '_data', '_prev'

    def __init__(self, data: D, prev: MB[SENode[D]]) -> None:
        self._data = data
        self._prev = prev

    def __iter__(self) -> Iterator[D]:
        node = self
        while node:
            yield node._data
            node = node._prev.get()
        yield node._data

    def __bool__(self) -> bool:
        return self._prev != MB()

    def data_eq(self, other: SENode[D]) -> bool:
        """Return true if other node has same or equal data."""
        if self._data is other._data:
            return True
        if self._data == other._data:
            return True
        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        return self._prev == other._prev and self.data_eq(other)

    def get_data(self) -> D:
        """Return contained data"""
        return self._data

    def fold[T](self, f: Callable[[T, D], T], init: T | None = None) -> T:
        """Reduce data across linked nodes.

        - with a function and an optional starting value
        - reduces in natural LIFO order
          - from self to the root

        """
        if init is None:
            acc: T = cast(T, self._data)
            node = self._prev.get()
        else:
            acc = init
            node = self

        while node:
            acc = f(acc, node._data)
            node = node._prev.get()
        acc = f(acc, node._data)
        return acc

    def pop2(self) -> tuple[D, MB[SENode[D]]]:
        """Return the data in the *head* and potential *tail*."""
        return self._data, self._prev

    def push_data(self, data: D) -> SENode[D]:
        """Push data onto the queue and return a new node containing the data."""
        return SENode(data, MB(self))
