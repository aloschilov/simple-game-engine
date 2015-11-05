try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache


from pathos.multiprocessing import Pool

# TODO: generate pool of all available processes
pool = Pool(processes=4)              # start 4 worker processes


def run_in_separate_process(default_value=None):

    class RunInSeparateProcess(object):
        def __init__(self, func):
            self.func = func
            self.args = None
            self.kwargs = None
            self.result = default_value
            self.async_result = None

        def __call__(self, *args, **kwargs):

            if self.async_result is None:

                # (self.async_result is None) tells us that there is no active calculation

                # Here we need to check that arguments hash has changed since the last run

                print "A call took place"

                if hash(self.args) != hash(args):
                    print "previous arguments does not match"
                    print "self.args = args"
                    self.args = args
                    print "self.kwargs = kwargs"
                    self.kwargs = kwargs
                    print ">> self.async_result = pool.apply_async(self.func, args, kwargs, self.callback)"
                    self.async_result = pool.apply_async(self.func, args, kwargs, self.callback)
                    print "<< self.async_result = pool.apply_async(self.func, args, kwargs, self.callback)"

            return self.result

        def callback(self, result):
            print "callback"
            self.async_result = None
            self.result = result

    return RunInSeparateProcess

