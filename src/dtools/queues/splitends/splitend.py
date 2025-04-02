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
### SplitEnd stack related data structures

With use I am finding this data structure needs some sort of supporting
infrastructure. Hence I split the original splitend module out to be its own
subpackage.

#### SplitEnd Stack type

- class SplitEnd: Singularly linked stack with shareable data nodes

"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Never, TypeVar
from dtools.fp.err_handling import MB
from .splitend_node import SENode as Node

__all__ = ['SplitEnd']

D = TypeVar('D')  # Not needed for mypy, hint for pdoc.
T = TypeVar('T')


class SplitEnd[D]:
    """Class SplitEnd

    LIFO stacks which can safely share immutable data between themselves.

    - each SplitEnd is a very simple stateful (mutable) LIFO stack
    - data can be pushed and popped to the stack
    - the first value pushed onto the SplitEnd becomes it "root"
    - different mutable split ends can safely share the same "tail"
    - each SplitEnd sees itself as a singularly linked list
    - bush-like datastructures can be formed using multiple SplitEnds
    - len() returns the number of elements on the SplitEnd stack
    - in boolean context, return true if split end is not rootless (empty)

    """

    __slots__ = '_count', '_top', '_root'

    def __init__(self, root: D, *ds: D) -> None:
        node = Node(root, MB[Node[D]]())
        self._root = MB(node)
        self._top, self._count = self._root, 1
        for d in ds:
            node = Node(d, self._top)
            self._top, self._count = MB(node), self._count + 1

    def __iter__(self) -> Iterator[D]:
        return iter(self._top.get())

    def __reversed__(self) -> Iterator[D]:
        return reversed(list(self))

    def __bool__(self) -> bool:
        # Returns true until all data is exhausted
        return bool(self._top.get())

    def __len__(self) -> int:
        return self._count

    def __repr__(self) -> str:
        return 'SplitEend(' + ', '.join(map(repr, reversed(self))) + ')'

    def __str__(self) -> str:
        return '>< ' + ' -> '.join(map(str, self)) + ' ||'

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self._count != other._count:
            return False

        left = self._top.get()
        right = other._top.get()
        for _ in range(self._count):
            if left is right:
                return True
            if not left.data_eq(right):
                return False
            if left:
                left = left._prev.get()
                right = right._prev.get()
        return True

    def push(self, *ds: D) -> None:
        """Push data onto the top of the SplitEnd."""
        for d in ds:
            node = Node(d, self._top)
            self._top, self._count = MB(node), self._count + 1

    def pop(self) -> D | Never:
        """Pop data off of the top of the SplitEnd.

        - re-root SplitEnd if root is popped off.

        """
        data, self._top, self._count = self._top.get().pop2() + (self._count - 1,)
        if self._count == 0:
            self._count, self._top = 1, self._root
        return data

    def peak(self) -> D:
        """Return the data at the top of the SplitEnd, doesn't consume it."""
        return self._top.get().get_data()

    def copy(self) -> SplitEnd[D]:
        """Return a copy of the SplitEnd.

        - O(1) space & time complexity.
        - returns a new instance with same data, including the root

        """
        se: SplitEnd[D] = SplitEnd(self._root.get().get_data())
        se._count, se._top, se._root = self._count, self._top, self._root
        return se

    def fold[T](self, f: Callable[[T, D], T], init: T | None = None, /) -> T | Never:
        """Reduce with a function, fold in natural LIFO Order."""
        if self._top:
            return self._top.get().fold(f, init)
        if init is not None:
            return init
        msg = 'SE: Folding empty SplitEnd but no initial value supplied'
        raise ValueError(msg)
