from engine import parallelization_decorator


@parallelization_decorator.run_in_separate_process(default_value=0.0)
def f(x):
    print "There was a call"
    x = 0
    for i in xrange(10000000):
        x = i
    print "sleep is over"
    return x*x

if __name__ == '__main__':
    for i in xrange(1000000000):
        f(10)
        if i % 100000 == 0:
            print f(10)
