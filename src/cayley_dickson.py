import pandas as pd
import itertools
import numbers

class KD(object):
    '''
    Implementation of Cayley-Dickson algebra. 
    Call it KD instead of CD because it sounds like it in my head.
    '''

    def __init__(self,a,b):
        self.a = a
        self.b = b

    # These two classes define the construction.
    def conjugate(self):
        return KD(self.a.conjugate(), -self.b)
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

    def __repr__(self):
        '''Without this custom implementation, the number of parentheses
        # is too damn high.'''
        a_s = str(self.a).replace("(","").replace(")","")
        b_s = str(self.b).replace("(","").replace(")","")
        return "({},{})".format(a_s,b_s)

    def __hash__(self):
        '''Hash is needed for pandas dataframes (I think).'''
        return hash((self.a,self.b))

    def zero_out(self):
        '''Creating a "zero" object requires recursion.'''
        if isinstance(self.a, numbers.Number):
            return KD(0,0)
        else:
            return KD(self.a.zero_out(), self.b.zero_out())

def expand_basis(basis):
    '''
    With an input basis, construct the basis set of the next
    iteration of the Cayley-Dickson construction. It will
    be twice as large as the original.
    '''

    first_term = basis[0]
    if isinstance(first_term, numbers.Number):
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
