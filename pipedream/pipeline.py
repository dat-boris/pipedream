import logging
from itertools import izip, tee
from functools import reduce, wraps
from inspect import isgeneratorfunction

logger = logging.getLogger(__name__)


class Pipeline(object):
    """
    A data pipeline example
    """
    def __init__(self, funcs):
        self.funcs = list(funcs)

    def apply(self, input, wrapper=None):
        """
        Compose a pipeline together
        """
        if wrapper:
            func_list = self.funcs
            if wrapper is not None:
                func_list = [wrapper(f) for f in self.funcs]

        # http://stackoverflow.com/questions/38755702/pythonic-way-to-chain-python-generator-function-to-form-a-pipeline
        return lambda x : reduce(lambda f, g : g(f), func_list, x)

    def monitor_apply(input, wrapper=None, error_store=None):
        """
        Not monitored yet
        """
        raise NotImplementedError("Have not created the error")


def monitor_step(step_func, validate_func):

    if (isgeneratorfunction(step_func)):
        @wraps(step_func)
        def wrapper(input, **kwargs):
            i1, i2 = tee(input)
            for i,o in izip(i1, step_func(i2)):
                try:
                    validate_func(o)
                except Exception as e:
                    logger.error("Seen error function: invalid output {} - {}".format(o, str(e)))
                    error_store.store_put(step_func, i, o)
                yield o
        return wrapper
    else:
        @wraps(step_func)
        def func_wrapper(input, **kwargs):
            output = step_func(input)
            try:
                validate_func(output)
            except Exception as e:
                logger.error("Seen error function: invalid output {} - {}".format(output, str(e)))
                error_store.store_put(step_func, input, output)
            return output
        return func_wrapper

def test_step(step_function, store):
    """
    Return the step function
    """
    for input, expected in store.all_data_for(step_function):
        logger.info(u"[TEST] Testing {} expects {}".format(input, expected))
        if (isgeneratorfunction(step_function)):
            assert list(step_function(input))==expected
        else:
            assert step_function(input)==expected
        logger.info(u"[TEST] Test passed for {}".format(step_function.__name__))
