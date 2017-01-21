from functools import reduce, wraps

# http://stackoverflow.com/questions/38755702/pythonic-way-to-chain-python-generator-function-to-form-a-pipeline
def compose_pipe(funcs, wrapper=None):
    """
    Compose a pipeline together
    """
    return lambda x : reduce(lambda f, g : g(f), list(funcs), x)


def save_fixture(step_func,
                     input_key_func=None,
                     output_key_func=None
                     ):
    @wraps(step_func)
    def wrapper(input, **kwargs):
        if key_func is None:
            import binascii
            # default we checksum the input in crc32
            key = binascii.crc32(input)
        output = step_func(input)
        # write the output into a key value store


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


