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

"""
### Developer Tools - Queue based data structures

#### Modules and sub-packages

- module dtools.queues.restrictive
  - mutable data structures geared to specific algorithmic use cases
    - FIFOQueue - First In First Out Queue
    - LIFOQueue - Last In First Out Queue
    - DoubleQueue - Double-ended Queue
- package dtools.splitends
  - mutable LIFO queues (stacks)
    - which still allow for data sharing between different instances

"""

__version__ = '0.26.0.0'
__author__ = 'Geoffrey R. Scheller'
__copyright__ = 'Copyright (c) 2023-2025 Geoffrey R. Scheller'
__license__ = 'Apache License 2.0'
