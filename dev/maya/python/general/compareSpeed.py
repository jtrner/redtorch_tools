"""
Compare speed

# test func1
func1()

# test func2
func2()
"""

# time a fucntion
def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap


# first funtcion to campare
@timing
def func1():
    # test for 500 times
    for i in xrange(500):
        mc.pointPosition('base.vtx[12]', w=True)


# second function to campare
@timing
def func2():
    # test for 500 times
    for i in xrange(500):
        mc.xform('base.vtx[12]', q=True, ws=True, t=True)

