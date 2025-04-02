# Copyright 2023-2024 Geoffrey R. Scheller
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

from __future__ import annotations
from dtools.fp.err_handling import MB
from dtools.queues.splitends.splitend_node import SENode as Node

class Test_Node:
    def test_bool(self) -> None:
        n1 = Node(1, MB())
        n2 = Node(2, MB(n1))

        assert not n1
        assert n2

    def test_linking(self) -> None:
        n1 = Node(1, MB())
        n2 = Node(2, MB(n1))
        n3 = Node(3, MB(n2))

        assert n3._data == 3
        assert n3._prev != MB()
        assert n3._prev.get()._data == 2
        assert n2._prev is not None
        assert n2._data == n3._prev.get()._data == 2
        assert n1._data == n2._prev.get()._data == n3._prev.get()._prev.get()._data == 1
        assert n3._prev != MB()
        assert n3._prev.get()._prev.get() != MB()
        assert n3._prev.get()._prev.get()._prev == MB()
        assert n3._prev.get()._prev == n2._prev

    def test_iter(self) -> None:
        n1 = Node(1, MB())
        n2 = Node(2, MB(n1))
        n3 = Node(3, MB(n2))
        n4 = Node(4, MB(n3))
        n5 = Node(5, MB(n4))

        value = 5
        for ii in n5:
            assert ii == value
            value -= 1

    def test_eq(self) -> None:
        a1 = Node(1, MB())
        a2 = Node(2, MB(a1))
        a3 = Node(3, MB(a2))
        a4 = Node(4, MB(a3))
        a5 = Node(5, MB(a4))
        
        b1 = Node(1, MB())
        b2 = Node(2, MB(b1))
        b3 = Node(3, MB(b2))
        b4 = Node(4, MB(b3))

        c2 = Node(2, MB(b1))
        c3 = Node(3, MB(b1))

        d2 = Node(2, MB(a1))
        d3 = Node(3, MB(d2))
        d4 = Node(42, MB(d3))
        d5 = Node(5, MB(d4))

        assert a1 == a1
        assert a1 != a2
        assert a1 == b1
        assert a5 != b4
        assert a4 == b4
        assert b2 == c2
        assert b2 != c3
        assert d2 == b2
        assert d3 == a3
        assert d3 == b3
        assert d4 != b4
        assert d5 != a5

    def test_fold(self) -> None:
        a1 = Node(1, MB())
        a2 = Node(2, MB(a1))
        a3 = Node(3, MB(a2))
        a4 = Node(4, MB(a3))
        a5 = Node(5, MB(a4))

        assert a4.fold(lambda x,y: x+y) == 10
        assert a4.fold(lambda x,y: x+y, 32) == 42
        assert a5.fold(lambda x,y: x+y) == 15

        b1 = Node(1, MB())
        b2 = Node(2, MB(b1))
        b3 = Node(5, MB(b2))
        b4 = Node(2, MB(b3))

        assert b4.fold(lambda x,y: x*y) == 20
        assert b4.fold(lambda x,y: x*y, 2.1) == 42.0
