
# PipeDream - a promise for Validation Driven Data

[![CircleCI](https://circleci.com/gh/sketchytechky/pipedream.svg?style=svg)](https://circleci.com/gh/sketchytechky/pipedream)

PipeDream is an initiative for creating a Validation Driven Data pipeline.

We propose a set of principle which helps us to create a Validation Driven Data
framework.  We illustrate this proposal with a set of libraries implemented against
the pipeline.

## Examples

See [word count example here](examples/01_word_count/)


## Principle of PipeDream

### 1. Functional composition

[Example](examples/01_word_count/s02_functional.py)

Processes should be composed in functional steps.  Error handling should be handled
by the pipeline to provide defensive programming.

```python
datapipe = pipeline.Pipeline([
    emit_words,
    filter_empty_word,
    count_words
])
```


### 2. Testability

Each processes, should be testable individually via [parameterize tests](http://doc.pytest.org/en/latest/parametrize.html)

```python
@pytest.mark.parametrize('desc,in,out', [
    ('Basic counting',
      'Hello world! Hello friends!',
      {'Hello':2, 'world':1, 'friends':1}
    ),
    ('Counting with unicode',
      'Hello world🌏, Hello friends🍕',
      {'Hello':2, 'world':1, 'friends':1}
    )
])
def test_count_of_words(desc,in,out):
    assert create_count_of_words(in) == out, "{} is correct".format(desc)
```


### 3. Real data testing

[Example](examples/01_word_count/s03_test_fixtures.py)

We should encourage testing using real data and large data set.  The framework
should be able to take in real data set and spit out test data at each stage

```python
import pipedream

store = PipelineStore('./test_fixture')

fixture_pipeline.apply(
    test_data,
    wrapper=store.save_fixture
)

# Test data is now stored in `./test_fixture`

# Each steps can be tested individually
pipeline.test_step(
    s02_functional.emit_words,
    store=store
)
```



### 5. Production monitoring

[Example](examples/01_word_count/s04_monitor_live.py)

We should be able to emit data health metrics for free in the pipeline, and use
such metrics in case of error

In case of abnormality, again such capturing is important to allow us to enable
automatic error capture

```python

monitored_pipeline = pipeline.Pipeline()
monitored_pipeline.set_steps([
    monitored_pipeline.monitor_step(
        s02_functional.emit_words,
        FrequencyValidator().validate
    ),
    monitored_pipeline.monitor_step(
        s02_functional.filter_empty_word,
        check_word_maxlen
    ),
    s02_functional.filter_empty_word,
    s02_functional.count_words
])

output = monitored_pipeline.monitor_apply(
    BAD_INPUT[0],
    error_prefix='error_store'
)

```


-------------


## What is Validation Driven Data?

> Data validation is the process of ensuring that a program operates on clean, correct and useful data
> [Wikipedia](https://en.wikipedia.org/wiki/Data_validation)

This process is often done at the end of data pipeline creation process, and
done overtime with observation of data to ensure that it behaves correctly.


#### What is the issue with carrying validation at the end?

It is often the approach that the validation will be carried out manually, as an
after thought on the data pipeline.

This create a few issues:

* Since the pipeline is not defined as validation in mind, the **validation becomes
  difficult** as it comes an after thought to carry out

* The developer find it difficult to debug in individual steps, since each process
  of the pipeline could be tightly coupled and it becomes difficult to make
  **small incremental steps during development**

* Since validation is manually done after, it is hard to guard against **regression
  of data**.  Once bug is found, it would be extra work to manually goes back and
  create test fixture.

* On uncaught error that cause failure, it will be time-consuming and difficult
  to reproduce each step of the data.

Note that this is not dissimilar to the argument for *Test driven development*
where test should be developed in first place, and that we should be apply a lot
of the same principle.



### Other want to have

Data-engineering-y

* This frameworkwork should be compatible with concurrency infrastructure of python3 such as [futures](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Future) and [coroutines`(https://docs.python.org/3/library/asyncio-task.html)

* There should be ability to `tag` a fixture - a classic use case is when we switch
data pipeline, we would like to be able to reuse and compare inputs / outputs between
pipeline.

```python
test_migration(old_data, old_expected):
  test_old_pipeline(patch_input_difference(old_data)) == old_expected
```


Data-science-cy

* We should be able to use the keyspace feature to do some key validation

* We should provide some "validation coverage" description - in a way provide
  statistics which allow us to identify missing validation and interesting outliers
