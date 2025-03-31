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

* class SplitEnd: Singularly linked stack with shareable data nodes

"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Never, TypeVar
from dtools.fp.err_handling import MB
from .splitend_node import _SENode as Node

__all__ = ['SplitEnd']

D = TypeVar('D')  # Not needed for mypy, hint for pdoc.
T = TypeVar('T')


class SplitEnd[D]:
    """Class SplitEnd

    LIFO stacks which can safely share immutable data between themselves.

    * each SplitEnd is a very simple stateful (mutable) LIFO stack
    * data can be pushed and popped to the stack
    * different mutable split ends can safely share the same "tail"
    * each SplitEnd sees itself as a singularly linked list
    * bush-like datastructures can be formed using multiple SplitEnds
    * len() returns the number of elements on the SplitEnd stack
    * in boolean context, return true if split end is not empty

    """

    __slots__ = '_count', '_top', '_root'

    def __init__(self, *ds: D) -> None:
        self._count = 0
        self._top: MB[Node[D]] = MB()
        self._root: MB[Node[D]] = MB()
        if len(ds) > 0:
            node = Node(ds[0], self._top)
            self._top = self._root = MB(node)
            self._count = 1
            for d in ds[1:]:
                node = Node(d, self._top)
                self._top, self._count = MB(node), self._count + 1

    def __iter__(self) -> Iterator[D]:
        if self._top == MB():
            empty: tuple[D, ...] = ()
            return iter(empty)
        return iter(self._top.get())

    def __reversed__(self) -> Iterator[D]:
        return reversed(list(self))

    def __bool__(self) -> bool:
        # Returns true if not a root node
        return bool(self._top)

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
        if self._count == 0:
            return True

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
        if len(ds) > 0:
            node = Node(ds[0], self._top)
            if self._top:
                self._top, self._count = MB(node), self._count + 1
            else:
                self._top = self._root = MB(node)
                self._count = 1
            for d in ds[1:]:
                node = Node(d, self._top)
                self._top, self._count = MB(node), self._count + 1

    def pop(self) -> MB[D]:
        """Pop data off of the top of the SplitEnd.

        Return MB of top data, if not empty, otherwise return MB().

        """
        if self._count > 0:
            data, self._top, self._count = self._top.get().pop2() + (self._count - 1,)
            if self._count == 0:
                self._root = self._top
            return MB(data)
        return MB()

    def peak(self, default: D | None = None, /) -> D:
        """Return the data at the top of the SplitEnd.

        * does not consume the data
        * raises ValueError if peaking at an empty SplitEnd

        """
        if self._count == 0:
            if default is None:
                raise ValueError('SE: Popping from an empty SplitEnd')
            return default
        return self._top.get().get_data()

    def copy(self) -> SplitEnd[D]:
        """Return a copy of the SplitEnd.

        * O(1) space & time complexity.
        * returns a new instance

        """
        se: SplitEnd[D] = SplitEnd()
        se._top, se._count = self._top, self._count
        return se

    def fold[T](self, f: Callable[[T, D], T], init: T | None = None, /) -> T | Never:
        """Reduce with a function.

        * folds in natural LIFO Order

        """
        if self._top != MB():
            return self._top.get().fold(f, init)
        if init is not None:
            return init
        msg = 'SE: Folding empty SplitEnd but no initial value supplied'
        raise ValueError(msg)
