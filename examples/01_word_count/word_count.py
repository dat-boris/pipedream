#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six
import io
import re

from collections import Counter

import sys
sys.path.append('../..')

from pipedream import pipeline
from pipedream import test as pipeline_test
from pipedream import store as pipeline_store


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

def map_reduce_count(stream):
    """
    How would we scale and distribute a wordcount operation
    """
    datapipe = pipeline.compose_pipe([
        emit_words,
        filter_empty_word,
        count_words
    ])

    return datapipe(iter(lambda: stream.read(1), ''))


#--------------------
# Example 4 - demo testing
#--------------------

def demo_test_fixture():
    # generate the tests
    create_fixture_pipeline = pipeline.compose_pipe([
            emit_words,
            filter_empty_word,
            count_words
        ],
        wrapper=pipeline.save_fixture
    )

    # py.test - boom!
    # run the tests
    test_fixture_pipeline = pipeline.compose_pipe([
            emit_words,
            filter_empty_word,
            count_words
        ],
        wrapper=pipeline_test.test_step
    )

MAX_WORD_LEN = 10

def demo_broken_monitoring(unexpected_input='xyz'):

    monitored_pipeline = pipeline.compose_pipe([
        emit_words,
        filter_empty_word,
        pipeline.monitor_step(
            lambda word: 0 < len(word) < MAX_WORD_LEN,
            input_key_func=None,
            output_key_func=None
        ),
        count_words
    ])
    monitored_pipeline(unexpected_input)

    # Run unexpected input
    errors = pipeline_store.list(store='prod_error')
    print(errors)

    pipeline_store.add_fixture('prod', 'test', errors[0])

    test_fixture_pipeline = pipeline.compose_pipe([
            emit_words,
            filter_empty_word,
            count_words
        ],
        wrapper=pipeline_test.test_step
    )


EXAMPLE_DATA = [
    u"Hello world! Hello friends!",
    u"Hello world🌏, Hello friends🍕",
]

def run_example(i, count_function):
    print("Running example: {}".format(i))
    for input_str in EXAMPLE_DATA:
        print(count_function(io.StringIO(input_str)))

if __name__=='__main__':
    run_example(1, count)
    run_example(2, count_better_parser)
    run_example(3, map_reduce_count)

    demo_test_fixture()
    demo_broken_monitoring()
    pipeline_store.review('key_here')
