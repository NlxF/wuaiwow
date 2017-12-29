class LazyProperty(object):
    """
    A descriptor protocol implementation used for wrapping a lambda
    function (without parameters) to behave like property access.
    Usage, only within a class definition: all_users = LazyProperty(lambda: [])
    """
    @staticmethod
    def is_lambda(v):
        lambda_example = lambda: 0
        return isinstance(v, type(lambda_example)) and v.__name__ == lambda_example.__name__

    @staticmethod
    def has_params(v):
        return len(inspect.getargspec(v).args) > 0

    def __init__(self, *args, **kwargs):
        for value in args:
            if LazyProperty.is_lambda(value):
                if LazyProperty.has_params(value):
                    raise Exception('Lambda function parameters are not allowed.')
                self.func = value
                return
        if not getattr(self, 'func', None):
            raise Exception('A LazyProperty instance should be initialized with a lambda function.')

    def __get__(self, *args, **kwargs):
        if not getattr(self, 'res', None):
            self.res = self.func()
        return self.res
