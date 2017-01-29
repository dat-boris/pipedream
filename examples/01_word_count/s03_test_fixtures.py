#!/usr/bin/env python

"""
This is how we would create the text fixture for each part of examples
"""

import s02_functional

from pipedream import pipeline

from pipedream import test as pipeline_test
from pipedream import store as pipeline_store

def demo_test_fixture():
    # generate the tests
    create_fixture_pipeline = pipeline.compose_pipe([
            s02_functional.emit_words,
            s02_functional.filter_empty_word,
            s02_functional.count_words
        ],
        wrapper=pipeline.save_fixture
    )

    # py.test - boom!
    # run the tests
    test_fixture_pipeline = pipeline.compose_pipe([
            s02_functional.emit_words,
            s02_functional.filter_empty_word,
            s02_functional.count_words
        ],
        wrapper=pipeline_test.test_step
    )


if __name__=='__main__':
    demo_test_fixture()
