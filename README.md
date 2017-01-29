
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

Processes should be composed in [Promise like pipeline](https://promisesaplus.com/)
which allows chaining of processes and error handler.

```python
# optional sync await can apply here
def production_pipeline(input):
    output = create_count_of_words(text)
                .then(aggregate_count)
                .catch(error_handler)
    return output
```


### 2. Testability

Each processes, should be testable individually via [parameterize tests](http://doc.pytest.org/en/latest/parametrize.html)

```python
@pytest.mark.parametrize('desc,in,out', [
    ('Basic counting', 'apple orange apple', {'apple':2, orange:1})
    ('Counting empty string', '', {})
])
def test_count_of_words(desc,in,out):
    assert create_count_of_words(in) == out, "{} is correct".format(desc)
```


### 3. Real data testing

We should encourage testing using real data and large data set.  The framework
should be able to take in real data set and spit out test data at each stage

```python
import pipedream

pipedream.set_fixture_capture(True,
                              number_of_keys=500,
                              output_fixture_dir='test_fixture')

# this will create the new_fixture dir
def production_pipeline(input):
    output = create_count_of_words(text)
                .set_partition_key_space(get_keyspace, get_data_given_key )
                .then(aggregate_count)
                .catch(error_handler)
    return output

def get_keyspace(data):
    return data.keys()

def get_data_given_key(key, data):
    return { key: data[key] }

@pipedream.use_fixture('create_count_of_words')
def test_with_fixture(test_fixture, test_output):
    # might need to do required mock/masking of test_output
    assert create_count_of_words(test_fixture) == test_output
```


### 4. Defensive failure and Automatic error capture

If we encounter error at each stage at production, we should be able to create
additional fixture from logs

```python
import pipedream

pipedream.set_error_fixture(True, output_as_log=True)

# this will create the log as serialized text which can be parsed and recreate break fixture
production_pipeline(input)

# Depends on how big your log is
parse_log_generate_fixture(logs,
                           error_reason='Example explanation',
                           output_fixture_dir='test_fixture')

```


### 5. Production monitoring

We should be able to emit data health metrics for free in the pipeline, and use
such metrics in case of error

In case of abnormality, again such capturing is important to allow us to enable
automatic error capture

```python

pipedream.set_error_fixture(True,
                            output_as_log=True,
                            log_assert_error=True)

# optional sync await can apply here
def production_pipeline(input_from_appleland):
    output = create_count_of_words(text)
                .metrics(count_apple_and_oranges)   # this get emitted metrics logger (e.g. statsd)
                .assert_metric(lambda metrics: metrics['apple_count'] > metrics['orange_count'])
                .then(aggregate_count)
                .catch(error_handler)
    return output
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
