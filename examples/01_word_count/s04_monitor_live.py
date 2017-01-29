#!/usr/bin/env python

"""
How we can send signal and review incidence
"""

import s02_functional

from pipedream import pipeline

from pipedream import test as pipeline_test
from pipedream import store as pipeline_store


MAX_WORD_LEN = 10

def demo_broken_monitoring(unexpected_input='xyz'):

    monitored_pipeline = pipeline.compose_pipe([
        s02_functional.emit_words,
        s02_functional.filter_empty_word,
        pipeline.monitor_step(
            lambda word: 0 < len(word) < MAX_WORD_LEN,
            input_key_func=None,
            output_key_func=None
        ),
        s02_functional.count_words
    ])
    monitored_pipeline(unexpected_input)

    # Run unexpected input
    errors = pipeline_store.list(store='prod_error')
    print(errors)

    pipeline_store.add_fixture('prod', 'test', errors[0])

    test_fixture_pipeline = pipeline.compose_pipe([
            s02_functional.emit_words,
            s02_functional.filter_empty_word,
            s02_functional.count_words
        ],
        wrapper=pipeline_test.test_step
    )


if __name__ == '__main__':
    demo_broken_monitoring()
    pipeline_store.review('key_here')
