#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six
import io
import re
from collections import Counter
from itertools import chain
from functools import reduce

#--------------------
# Example 1 - niave example
#--------------------

RE_SPACE = re.compile('\s')

def count(stream):
    """
    How we currently do wordcount
    """
    counter = Counter()
    word = ''
    for i,char in enumerate(iter(lambda: stream.read(1), '')):
        if char is None:
            break
        if RE_SPACE.match(char):
            if word:
                counter[word] += 1
                word = ''
        else:
            word += char
    if word:
        counter[word] += 1
    return counter

#--------------------
# Example 2 - edge case sampling
#--------------------

RE_CHAR = re.compile('\w')

def count_better_parser(stream):
    """
    How we currently do wordcount with unicode
    - edge case: unicode
    """
    counter = Counter()
    word = ''
    for i,char in enumerate(iter(lambda: stream.read(1), '')):
        if char is None:
            break
        if not RE_CHAR.match(char):
            if word:
                counter[word] += 1
                word = ''
        else:
            word += char
    if word:
        counter[word] += 1
    return counter


#--------------------
# Example 3 - functional example
#--------------------

# http://stackoverflow.com/questions/38755702/pythonic-way-to-chain-python-generator-function-to-form-a-pipeline
def compose(*funcs):
    return lambda x : reduce(lambda f, g : g(f), list(funcs), x)

def map_reduce_count(stream):
    """
    How would we scale and distribute a wordcount operation
    """
    def emit_words(stream):
        """
        Return a generator of words
        """
        word = ''
        for char in stream:
            if char is None:
                break
            if not RE_CHAR.match(char):
                yield word
                word = ''
            else:
                word += char
        yield word

    def filter_empty_word(word_stream):
        """
        Filter out empty words
        - principle one, edge case should be handled by separate function
        - Note: can be replace by ifilter
        """
        for word in word_stream:
            if word:
                yield word

    def count_words(word_stream):
        """
        Filter out empty words
        """
        counter = Counter()
        for word in word_stream:
            counter[word] += 1
        return counter

    pipeline = compose(
        emit_words,
        filter_empty_word,
        count_words
    )

    return pipeline(iter(lambda: stream.read(1), ''))


#--------------------
# Example 4 - functional example
#--------------------

def tested_wordcount(file):
    """
    """
    pass


EXAMPLE_DATA = [
    u"Hello world! Hello friends!",
    u"Hello world🌏, Hello friends🍕"
]

def run_example(i, count_function):
    print("Running example: {}".format(i))
    for input_str in EXAMPLE_DATA:
        print(count_function(io.StringIO(input_str)))

if __name__=='__main__':
    run_example(1, count)
    run_example(2, count_better_parser)
    run_example(3, map_reduce_count)
