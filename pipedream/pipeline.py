import logging
from functools import reduce, wraps
from inspect import isgeneratorfunction

logger = logging.getLogger(__name__)

def compose_pipe(funcs, wrapper=None):
    """
    Compose a pipeline together
    """
    func_list = list(funcs)
    if wrapper is not None:
        func_list = [wrapper(f) for f in funcs]
    # http://stackoverflow.com/questions/38755702/pythonic-way-to-chain-python-generator-function-to-form-a-pipeline
    return lambda x : reduce(lambda f, g : g(f), func_list, x)

def monitor_step(validate_func,
                     input_key_func=None,
                     output_key_func=None
                     ):
    @wraps(validate_func)
    def wrapper(input, **kwargs):
        for i in input:
            if (validate_func(i)):
                yield i
    return wrapper

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
