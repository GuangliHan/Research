#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#   Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
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

"""vocabulary utils from rat-sql: https://github.com/Microsoft/rat-sql"""

import collections
import collections.abc
import json
import operator

UNK = '<UNK>'
BOS = '<BOS>'
EOS = '<EOS>'


class Vocab(collections.abc.Set):
    """Vocab"""

    def __init__(self, iterable, special_elems=(UNK, BOS, EOS)):
        """__init__"""
        # type: (Iterable[T]) -> None
        elements = list(special_elems)
        elements.extend(iterable)
        assert len(elements) == len(set(elements))

        self.id_to_elem = {i: elem for i, elem in enumerate(elements)}
        self.elem_to_id = {elem: i for i, elem in enumerate(elements)}

    def __iter__(self):
        """__iter__"""
        # type: () -> Iterator[Union[T, IndexedSet.Sentinel]]
        for i in range(len(self)):
            yield self.id_to_elem[i]

    def __contains__(self, value):
        """__contains__"""
        # type: (object) -> bool
        return value in self.elem_to_id

    def __len__(self):
        """__len__"""
        # type: () -> int
        return len(self.elem_to_id)

    def __getitem__(self, key):
        """__getitem__"""
        # type: (int) -> Union[T, IndexedSet.Sentinel]
        if isinstance(key, slice):
            raise TypeError('Slices not supported.')
        return self.id_to_elem[key]

    def index(self, value):
        """index"""
        # type: (T) -> int
        try:
            return self.elem_to_id[value]
        except KeyError:
            return self.elem_to_id[UNK]

    def indices(self, values):
        """indices"""
        # type: (Iterable[T]) -> List[int]
        return [self.index(value) for value in values]

    def __hash__(self):
        """__hash__"""
        # type: () -> int
        return id(self)

    @classmethod
    def load(self, in_path):
        """load"""
        return Vocab(json.load(open(in_path)), special_elems=())

    def save(self, out_path):
        """save"""
        with open(out_path, 'w') as ofs:
            json.dump([self.id_to_elem[i] for i in range(len(self.id_to_elem))], ofs)


class VocabBuilder:
    """VocabBuilder"""
    def __init__(self, min_freq=None, max_count=None):
        """__init__"""
        self.word_freq = collections.Counter()
        self.min_freq = min_freq
        self.max_count = max_count

    def add_word(self, word, count=1):
        """add_word"""
        self.word_freq[word] += count

    def finish(self, *args, **kwargs):
        """finish"""
        # Select the `max_count` most frequent words. If `max_count` is None, then choose all of the words.
        eligible_words_and_freqs = self.word_freq.most_common(self.max_count)
        if self.min_freq is not None:
            for i, (word, freq) in enumerate(eligible_words_and_freqs):
                if freq < self.min_freq:
                    eligible_words_and_freqs = eligible_words_and_freqs[:i]
                    break

        return Vocab(
                    (word for word, freq in sorted(eligible_words_and_freqs)), 
                    *args, **kwargs)
    
    def save(self, path):
        """save"""
        with open(path, "w") as f:
            json.dump(self.word_freq, f)
    
    def load(self, path):
        """load"""
        with open(path, "r") as f:
            self.word_freq = collections.Counter(json.load(f))
