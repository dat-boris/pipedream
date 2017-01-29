#!/usr/bin/env python

"""
Breaking down into functional calls
"""

#import six
import re

from collections import Counter

import sys
sys.path.append('../..')

from pipedream import pipeline
from testdata import run_example

RE_CHAR = re.compile('\w')

def functional_counts(stream):
    """
    How would we scale and distribute a wordcount operation
    """
    datapipe = pipeline.Pipeline([
        emit_words,
        filter_empty_word,
        count_words
    ])

    return datapipe.apply(iter(lambda: stream.read(1), ''))


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
    return dict(counter)


if __name__=='__main__':
    run_example(3, functional_counts)
