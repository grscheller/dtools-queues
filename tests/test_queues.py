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
from typing import Optional
from dtools.circular_array import ca
from dtools.queues.de import DEQueue as DQ
from dtools.queues.de import de_queue as dq
from dtools.queues.fifo import FIFOQueue as FQ
from dtools.queues.fifo import fifo_queue as fq
from dtools.queues.lifo import LIFOQueue as LQ
from dtools.queues.lifo import lifo_queue as lq
from dtools.containers.maybe import MayBe as MB

class TestQueueTypes:
    def test_mutate_map(self) -> None:
        dq1: DQ[int] = DQ()
        dq1.pushl(1,2,3)
        dq1.pushr(1,2,3)
        dq2 = dq1.map(lambda x: x-1)
        assert dq2.popl() == dq2.popr() == MB(2)

        def add_one_if_int(x: int|str) -> int|str:
            if type(x) is int:
                return x+1
            else:
                return x

        fq1: FQ[int] = FQ()
        fq1.push(1,2,3)
        fq1.push(4,5,6)
        fq2 = fq1.map(lambda x: x+1)
        not_none = fq2.pop()
        assert not_none != MB()
        assert not_none == MB(2)
        assert fq2.peak_last_in() == MB(7) != MB()
        assert fq2.peak_next_out() == MB(3)

        lq1: LQ[MB[int]] = LQ()  # not really a canonical way to use MB
        lq1.push(MB(1), MB(2), MB(3))
        lq1.push(MB(4), MB(), MB(5))
        lq2 = lq1.map(lambda mb: mb.bind(lambda n: MB(2*n)))
        last = lq2.pop()
        assert last.get(MB(42)) == MB(10)
        pop_out = lq2.pop()
        assert pop_out == MB(MB())
        assert pop_out.get(MB(42)) == MB()
        assert lq2.peak() == MB(MB(8))
        assert lq2.peak().get(MB(3)) == MB(8)
        assert lq2.peak().get(MB(3)).get(42) == 8

    def test_push_then_pop(self) -> None:
        dq1 = DQ[int]()
        pushed_1 = 42
        dq1.pushl(pushed_1)
        popped_1 = dq1.popl()
        assert MB(pushed_1) == popped_1
        assert len(dq1) == 0
        pushed_1 = 0
        dq1.pushl(pushed_1)
        popped_1 = dq1.popr()
        assert pushed_1 == popped_1.get(-1) == 0
        assert not dq1
        pushed_1 = 0
        dq1.pushr(pushed_1)
        popped_2 = dq1.popl().get(1000)
        assert popped_2 != 1000
        assert pushed_1 == popped_2
        assert len(dq1) == 0

        dq2: DQ[str] = DQ()
        pushed_3 = ''
        dq2.pushr(pushed_3)
        popped_3 = dq2.popr().get('hello world')
        assert pushed_3 == popped_3
        assert len(dq2) == 0
        dq2.pushr('first')
        dq2.pushr('second')
        dq2.pushr('last')
        assert dq2.popl() == MB('first')
        assert dq2.popr() == MB('last')
        assert dq2
        dq2.popl()
        assert len(dq2) == 0

        fq1: FQ[MB[int|str]] = FQ()
        fq1.push(MB(42))
        fq1.push(MB('bar'))
        assert fq1.pop().get() == MB(42)
        assert fq1.pop().get(MB('foo')).get(13) == 'bar'
        assert fq1.pop().get(MB('foo')).get() == 'foo'
        assert len(fq1) == 0
        fq1.push(MB(0))
        assert fq1.pop() == MB(MB(0))
        assert not fq1
        assert fq1.pop() == MB()
        assert len(fq1) == 0
        val: MB[int|str] = MB('Bob' + 'by')
        fq1.push(val)
        assert fq1
        assert val.get('Robert') == fq1.pop().get(MB('Bob')).get('Billy Bob') == 'Bobby'
        assert len(fq1) == 0
        assert fq1.pop().get(MB('Robert')) == MB('Robert')
        fq1.push(MB('first'))
        fq1.push(MB(2))
        fq1.push(MB('last'))
        fq1.map(lambda x: x.get('improbable'))
        popped = fq1.pop()
        if popped == 'impossible' or popped == 'improbable':
            assert False
        else:
            assert popped.get().get('impossible') == 'first'
        assert fq1.pop().get(MB()).get(-1) == 2
        assert fq1
        fq1.pop()
        assert len(fq1) == 0
        assert not fq1

        lq10: LQ[int|float|str] = LQ()
        lq10.push(42)
        lq10.push('bar')
        assert lq10.pop().get(100) == 'bar'
        assert lq10.pop().get('foo') == 42
        assert lq10.pop().get(24.0) == 24.0
        assert len(lq10) == 0
        lq10.push(0)
        assert lq10.pop() == MB(0)
        assert not lq10
        assert lq10.pop() == MB()
        assert len(lq10) == 0

        val1: int|float|complex = 1.0 + 2.0j
        val2: int|float|complex = 2
        val3: int|float|complex = 3.0
        fq11: FQ[int|float|complex] = FQ()
        lq11: LQ[int|float|complex] = LQ()
        lq11.push(val1)
        lq11.push(val2)
        lq11.push(val3)
        fq11.push(val1)
        fq11.push(val2)
        fq11.push(val3)
        assert lq11.pop().get() * lq11.pop().get() == 6.0
        assert fq11.pop().get() * fq11.pop().get() == 2.0 + 4.0j


        def is42(ii: int) -> Optional[int]:
            return None if ii == 42 else ii

        fq2: FQ[object] = FQ()
        fq3: FQ[object] = FQ()
        fq2.push(None)
        fq3.push(None)
        assert fq2 == fq3
        assert len(fq2) == 1

        barNone: tuple[int|None, ...] = (None, 1, 2, 3, None)
        bar42 = (42, 1, 2, 3, 42)
        fq4: FQ[object] = FQ(barNone)
        fq5: FQ[object] = FQ(map(is42, bar42))
        assert fq4 == fq5

        lqu1: LQ[Optional[int]] = LQ()
        lqu2: LQ[Optional[int]] = LQ()
        lqu1.push(None, 1, 2, None)
        lqu2.push(None, 1, 2, None)
        assert lqu1 == lqu2
        assert len(lqu1) == 4

        barNone = (None, 1, 2, None, 3)
        bar42 = (42, 1, 2, 42, 3)
        lqu3: LQ[Optional[int]] = LQ(barNone)
        lqu4: LQ[Optional[int]] = LQ(map(is42, bar42))
        assert lqu3 == lqu4


    def test_pushing_None(self) -> None:
        dq1: DQ[Optional[int]] = DQ()
        dq2: DQ[Optional[int]] = DQ()
        dq1.pushr(None)
        dq2.pushl(None)
        assert dq1 == dq2

        def is42(ii: int) -> Optional[int]:
            return None if ii == 42 else ii

        barNone = (1, 2, None, 3, None, 4)
        bar42 = (1, 2, 42, 3, 42, 4)
        dq3 = DQ[Optional[int]](barNone)
        dq4 = DQ[Optional[int]](map(is42, bar42))
        assert dq3 == dq4

    def test_bool_len_peak(self) -> None:
        dq: DQ[int] = DQ()
        assert not dq
        dq.pushl(2,1)
        dq.pushr(3)
        assert dq
        assert len(dq) == 3
        assert dq.popl() == MB(1)
        assert len(dq) == 2
        assert dq
        assert dq.peakl() == MB(2)
        assert dq.peakr() == MB(3)
        assert dq.popr() == MB(3)
        assert len(dq) == 1
        assert dq
        assert dq.popl() == MB(2)
        assert len(dq) == 0
        assert not dq
        assert len(dq) == 0
        assert not dq
        dq.pushr(42)
        assert len(dq) == 1
        assert dq
        assert dq.peakl() == MB(42)
        assert dq.peakr() == MB(42)
        assert dq.popr() == MB(42)
        assert not dq
        assert dq.peakl() == MB()
        assert dq.peakr() == MB()

        fq: FQ[int] = FQ()
        assert not fq
        fq.push(1,2,3)
        assert fq
        assert fq.peak_next_out() == MB(1)
        assert fq.peak_last_in() == MB(3)
        assert len(fq) == 3
        assert fq.pop() == MB(1)
        assert len(fq) == 2
        assert fq
        assert fq.pop() == MB(2)
        assert len(fq) == 1
        assert fq
        assert fq.pop() == MB(3)
        assert len(fq) == 0
        assert not fq
        assert fq.pop().get(-42) == -42
        assert len(fq) == 0
        assert not fq
        fq.push(42)
        assert fq
        assert fq.peak_next_out() == MB(42)
        assert fq.peak_last_in() == MB(42)
        assert len(fq) == 1
        assert fq
        assert fq.pop() == MB(42)
        assert not fq
        assert fq.peak_next_out().get(-42) == -42
        assert fq.peak_last_in().get(-42) == -42

        lq: LQ[int] = LQ()
        assert not lq
        lq.push(1,2,3)
        assert lq
        assert lq.peak() == MB(3)
        assert len(lq) == 3
        assert lq.pop() == MB(3)
        assert len(lq) == 2
        assert lq
        assert lq.pop() == MB(2)
        assert len(lq) == 1
        assert lq
        assert lq.pop() == MB(1)
        assert len(lq) == 0
        assert not lq
        assert lq.pop() == MB()
        assert len(lq) == 0
        assert not lq
        lq.push(42)
        assert lq
        assert lq.peak() == MB(42)
        assert len(lq) == 1
        assert lq
        lq.push(0)
        assert lq.peak() == MB(0)
        popped = lq.pop()
        assert popped.get(-1) == 0
        assert lq.peak() == MB(42)
        popped2 = lq.pop().get(-1)
        assert popped2 == 42
        assert not lq
        assert lq.peak() == MB()
        assert lq.pop() == MB()

    def test_iterators(self) -> None:
        data_d = ca(1, 2, 3, 4, 5)
        data_mb = data_d.map(lambda d: MB(d))
        dq: DQ[MB[int]] = DQ(data_mb)
        ii = 0
        for item in dq:
            assert data_mb[ii] == item
            ii += 1
        assert ii == 5

        dq0: DQ[bool] = DQ()
        for _ in dq0:
            assert False

        data_bool_mb: tuple[bool, ...] = ()
        dq1: DQ[bool] = DQ(data_bool_mb)
        for _ in dq1:
            assert False
        dq1.pushr(True)
        dq1.pushl(True)
        dq1.pushr(True)
        dq1.pushl(False)
        assert not dq1.popl().get(True)
        while dq1:
            assert dq1.popl().get(False)
        assert dq1.popr() == MB()

        def wrapMB(x: int) -> MB[int]:
            return MB(x)

        data_ca = ca(1, 2, 3, 4, 0, 6, 7, 8, 9)
        fq: FQ[MB[int]] = FQ(data_ca.map(wrapMB))
        assert data_ca[0] == 1
        assert data_ca[-1] == 9
        ii = 0
        for item in fq:
            assert data_ca[ii] == item.get()
            ii += 1
        assert ii == 9

        fq0: FQ[MB[int]] = FQ()
        for _ in fq0:
            assert False

        fq00: FQ[int] = FQ(())
        for _ in fq00:
            assert False
        assert not fq00

        data_list: list[int] = list(range(1,1001))
        lq: LQ[int] = LQ(data_list)
        ii = len(data_list) - 1
        for item_int in lq:
            assert data_list[ii] == item_int
            ii -= 1
        assert ii == -1

        lq0: LQ[int] = LQ()
        for _ in lq0:
            assert False
        assert not lq0
        assert lq0.pop() == MB()

        lq00: LQ[int] = LQ(*())
        for _ in lq00:
            assert False
        assert not lq00
        assert lq00.pop() == MB()

    def test_equality(self) -> None:
        dq1: DQ[object] = dq(1, 2, 3, 'Forty-Two', (7, 11, 'foobar'))
        dq2: DQ[object] = dq(2, 3, 'Forty-Two')
        dq2.pushl(1)
        dq2.pushr((7, 11, 'foobar'))
        assert dq1 == dq2

        tup = dq2.popr().get(tuple(range(42)))
        assert dq1 != dq2

        dq2.pushr((42, 'foofoo'))
        assert dq1 != dq2

        dq1.popr()
        dq1.pushr((42, 'foofoo'))
        dq1.pushr(tup)
        dq2.pushr(tup)
        assert dq1 == dq2

        holdA = dq1.popl().get(0)
        holdB = dq1.popl().get(0)
        holdC = dq1.popr().get(0)
        dq1.pushl(holdB)
        dq1.pushr(holdC)
        dq1.pushl(holdA)
        dq1.pushl(200)
        dq2.pushl(200)
        assert dq1 == dq2

        tup1 = 7, 11, 'foobar'
        tup2 = 42, 'foofoo'

        fq1 = fq(1, 2, 3, 'Forty-Two', tup1)
        fq2 = fq(2, 3, 'Forty-Two')
        fq2.push((7, 11, 'foobar'))
        popped = fq1.pop()
        assert popped == MB(1)
        assert fq1 == fq2

        fq2.push(tup2)
        assert fq1 != fq2

        fq1.push(fq1.pop(), fq1.pop(), fq1.pop())
        fq2.push(fq2.pop(), fq2.pop(), fq2.pop())
        fq2.pop()
        assert MB(tup2) == fq2.peak_next_out()
        assert fq1 != fq2
        assert fq1.pop() != fq2.pop()
        assert fq1 == fq2
        fq1.pop()
        assert fq1 != fq2
        fq2.pop()
        assert fq1 == fq2

        l1 = ['foofoo', 7, 11]
        l2 = ['foofoo', 42]

        lq1: LQ[object] = lq(3, 'Forty-Two', l1, 1)
        lq2: LQ[object] = lq(3, 'Forty-Two', 2)
        assert lq1.pop() == MB(1)
        peak = lq1.peak().get([1,2,3,4,5])
        assert peak == l1
        assert type(peak) is list
        assert peak.pop() == 11
        assert peak.pop() == 7
        peak.append(42)
        assert lq2.pop() == MB(2)
        lq2.push(l2)
        assert lq1 == lq2

        lq2.push(42)
        assert lq1 != lq2

        lq3: LQ[str] = LQ(map(lambda i: str(i), range(43)))
        lq4: LQ[int] = lq(*range(-1, 39), 41, 40, 39)

        lq3.push(lq3.pop().get(), lq3.pop().get(), lq3.pop().get())
        lq5 = lq4.map(lambda i: str(i+1))
        assert lq3 == lq5

    def test_map(self) -> None:
        def f1(ii: int) -> int:
            return ii*ii - 1

        def f2(ii: int) -> str:
            return str(ii)

        dq0: DQ[int] = dq()
        dq1 = dq(5, 2, 3, 1, 42)
        dq2 = dq1.copy()
        assert dq2 == dq1
        assert dq2 is not dq1
        dq0m = dq0.map(f1)
        dq1m = dq2.map(f1)
        assert dq1 == dq(5, 2, 3, 1, 42)
        assert dq0m == dq()
        assert dq1m == dq(24, 3, 8, 0, 1763)
        assert dq0m.map(f2) == DQ()
        assert dq1m.map(f2) == dq('24', '3', '8', '0', '1763')

        fq0: FQ[int] = fq()
        fq1: FQ[int] = fq(5, 42, 3, 1, 2)
        q0m = fq0.map(f1)
        q1m = fq1.map(f1)
        assert q0m == fq()
        assert q1m == fq(24, 1763, 8, 0, 3)

        fq0.push(8, 9, 10)
        assert fq0.pop().get(-1) == 8
        assert fq0.pop() == MB(9)
        fq2 = fq0.map(f1)
        assert fq2 == fq(99)
        assert fq2 == fq(99)

        fq2.push(100)
        fq3 = fq2.map(f2)
        assert fq3 == FQ(['99', '100'])

        lq0: LQ[int] = LQ()
        lq1 = lq(5, 42, 3, 1, 2)
        lq0m = lq0.map(f1)
        lq1m = lq1.map(f1)
        assert lq0m == LQ()
        assert lq1m == lq(24, 1763, 8, 0, 3)

        lq0.push(8, 9, 10)
        assert lq0.pop() == MB(10)
        assert lq0.pop() == MB(9)
        lq2 = lq0.map(f1)
        assert lq2 == lq(63)

        lq2.push(42)
        lq3 = lq2.map(f2)
        assert lq3 == lq('63', '42')

    def test_folding(self) -> None:
        def f1(ii: int, jj: int) -> int:
            return ii + jj

        def f2l(ss: str, ii: int) -> str:
            return ss + str(ii)

        def f2r(ii: int, ss: str) -> str:
            return ss + str(ii)

        data = [1, 2, 3, 4, 5]
        dq0: DQ[int] = DQ()
        fq0: FQ[int] = FQ()
        lq0: LQ[int] = LQ()
        
        dq1: DQ[int] = DQ()
        fq1: FQ[int] = FQ()
        lq1: LQ[int] = LQ()

        dq1.pushr(*data[1:])
        dq1.pushl(data[0])
        fq1.push(*data)
        lq1.push(*data)

        assert dq1.foldl(f1).get(42) == 15
        assert dq1.foldr(f1).get(42) == 15
        assert fq1.fold(f1).get(42) == 15
        assert lq1.fold(f1).get(42) == 15

        assert dq1.foldl(f1, 10).get(-1) == 25
        assert dq1.foldr(f1, 10).get(-1) == 25
        assert fq1.fold(f1, 10).get(-1) == 25
        assert lq1.fold(f1, 10).get(-1) == 25

        assert dq1.foldl(f2l, '0').get('-1') == '012345'
        assert dq1.foldr(f2r, '6').get('-1') == '654321' 
        assert fq1.fold(f2l, '0').get('-1') == '012345'
        assert lq1.fold(f2l, '6').get('-1') == '654321'

        assert dq0.foldl(f1).get(42) == 42
        assert dq0.foldr(f1).get(42) == 42
        assert fq0.fold(f1).get(42) == 42
        assert lq0.fold(f1).get(42) == 42

        assert dq0.foldl(f1, 10).get(-1) == 10
        assert dq0.foldr(f1, 10).get(-1) == 10
        assert fq0.fold(f1, 10).get(-1) == 10
        assert lq0.fold(f1, 10).get(-1) == 10

        assert dq0.foldl(f2l, '0').get() == '0'
        assert dq0.foldr(f2r, '6').get() == '6' 
        assert fq0.fold(f2l, '0').get() == '0'
        assert lq0.fold(f2l, '6').get() == '6'

        cnt_up = fq1.fold(f2l, '0').map(lambda ss: ss + '6789')
        assert cnt_up == MB('0123456789')
