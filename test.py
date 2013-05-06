def minus(f):
    print 'minus'
    f()

def plus(f):
    print 'plus'
    f()

def test(a):
    if a > 3:return plus
    else:return minus

@test(2)
def func():
    print 'ok'
