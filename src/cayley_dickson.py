import pandas as pd
import functools
import itertools
import numbers

memoize_multiplication = True

def memoize(obj):
    cache = obj.cache = {}
    @functools.wraps(obj)
    def memoizer(*args):
        if args not in cache:
            cache[args] = obj(*args)
        return cache[args]
    def not_memoizer(*args):
        return obj(*args)

    return memoizer if memoize_multiplication else not_memoizer

def is_number(x):
    return isinstance(x, numbers.Number)

class KD(object):
    '''
    Implementation of Cayley-Dickson algebra. 
    Call it KD instead of CD because it sounds like it in my head.
    '''

    def __init__(self,a,b):
        self.a = a
        self.b = b
        self.terms = len(tuple(self))

    # These two classes, conjugate and __mul__, define the construction.
    def conjugate(self):
        return KD(self.a.conjugate(), -self.b)

    @memoize
    def __mul__(self, y):
        a,b = self.a, self.b
        c,d = y.a, y.b
        return KD(a*c - d.conjugate()*b, 
                  d*a + b*c.conjugate())
    def __neg__(self):
        return KD(-self.a,-self.b)
    def __add__(self,y):
        a,b = self.a, self.b
        c,d = y.a, y.b
        return KD(a+c,b+d)
    def __sub__(self,y):
        a,b = self.a, self.b
        c,d = y.a, y.b
        return KD(a-c,b-d)
    def __eq__(self,y):
        return self.a==y.a and self.b==y.b

    def __hash__(self):
        '''Hash is needed for pandas dataframes (I think).'''
        return hash((self.a,self.b))

    def zero_out(self):
        '''Creating a "zero" object requires recursion.'''
        if is_number(self.a):
            return KD(0,0)
        else:
            return KD(self.a.zero_out(), self.b.zero_out())

    def __iter__(self):
        if is_number(self.a):
            yield self.a
            yield self.b
            return
        for x in self.a:  yield x
        for y in self.b:  yield y

    def __repr__(self):
        '''Without this custom implementation, the number of parentheses
        is too damn high.'''
        return str(tuple(self))

    def group_index(self):
        '''Returns the index this would be in a group for a multipication
        table. For example, complex numbers 1=>0, i=>1, -1=>2, -i=>3.'''
        try:
            return tuple(self).index(1)
        except:
            pass
        try:
            return self.terms + tuple(self).index(-1)
        except:
            msg = "Not a unit direction"
            raise ValueError(msg)

def expand_basis(basis):
    '''
    With an input basis, construct the basis set of the next
    iteration of the Cayley-Dickson construction. It will
    be twice as large as the original.
    '''

    first_term = basis[0]
    if is_number(first_term):
        zero = 0
    else:
        zero = first_term.zero_out()
    for x in basis:
        yield KD(x,zero)
    for x in basis:
        yield KD(zero,x)

def KD_construction(basis):
    ''' 
    Given a basis set, construct the next  multipication table  of the 
    Cayley-Dickson construction.
    '''

    ex_basis = list(expand_basis(basis))
    K  = pd.DataFrame(index=ex_basis,columns=ex_basis)
    for a,b in itertools.product(ex_basis,repeat=2):
        K[a][b] = a*b
    return K

def cayley_index_name(x):
    ''' A "nice" set of names for the smaller systems. '''
    from ast import literal_eval
    val = literal_eval(str(x))

    # Complex names
    complex_names = {(1,0):'1',
                     (0,1):'i',
                     (-1,0):'-1',
                     (0,-1):'-i'}
    if val in complex_names:
        return complex_names[val]

    # Quaternion names
    q_names = {(1,0,0,0):'1',
               (0,1,0,0):'i',
               (0,0,1,0):'j',
               (0,0,0,1):'k',
               (-1,0,0,0):'-1',
               (0,-1,0,0):'-i',
               (0,0,-1,0):'-j',
               (0,0,0,-1):'-k'}

    if val in q_names:
        return q_names[val]

    return None
    

if __name__ == "__main__":

    # The reals
    real_basis = [1,]

    C = KD_construction(real_basis)
    print "Complex\n",C

    H = KD_construction(C.index)
    print "Quaternion\n",H

    #O = KD_construction(H.index)
    #print "Octonion\n",O

    #S = KD_construction(O.index)
    #print "Sedenion\n",S

    #T = KD_construction(S.index)
    #D = KD_construction(T.index)

    # Expected output
    '''
        Complex
               (1,0)   (0,1)
        (1,0)  (1,0)   (0,1)
        (0,1)  (0,1)  (-1,0)
        Quaternion
                   (1,0,0,0)   (0,1,0,0)   (0,0,1,0)   (0,0,0,1)
        (1,0,0,0)  (1,0,0,0)   (0,1,0,0)   (0,0,1,0)   (0,0,0,1)
        (0,1,0,0)  (0,1,0,0)  (-1,0,0,0)  (0,0,0,-1)   (0,0,1,0)
        (0,0,1,0)  (0,0,1,0)   (0,0,0,1)  (-1,0,0,0)  (0,-1,0,0)
        (0,0,0,1)  (0,0,0,1)  (0,0,-1,0)   (0,1,0,0)  (-1,0,0,0)
    '''
