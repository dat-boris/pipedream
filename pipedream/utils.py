from functools import wraps
#from itertools import izip, tee
from inspect import isgeneratorfunction

def wrap_function(f, callback):
    """
    A Wrapper function which saves each part into setting

    Parameters
    ----------
    callback: Function
        callback(input, output, func)
    """
    if isgeneratorfunction(f):
        @wraps(f)
        def generator_wrapper(input, **kwargs):
            output_list = []
            for output in f(input):
                yield output
                output_list.append(output)
            callback(input, output_list, f)
        return generator_wrapper

    else:
        @wraps(f)
        def func_wrapper(input, **kwargs):
            output = f(input)
            callback(input, output, f)
            return output
        return func_wrapper
